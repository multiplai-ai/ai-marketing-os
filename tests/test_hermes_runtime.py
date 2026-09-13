from __future__ import annotations

import json
import os
import pwd
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS = Path(__file__).parents[1] / "runtime" / "hermes" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from hermes_common import HermesError, canonical_child
import memory_review
import profile_backup
import render_agent_bundle
import runtime_reconcile
import task_runner
import workspace_manager
import writer_lease
import effect_broker
import effect_socket


def executable(path: Path, body: str) -> Path:
    path.write_text("#!/bin/sh\nset -eu\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path


@pytest.fixture
def git_remote(tmp_path):
    seed = tmp_path / "seed"; remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-b", "main", seed], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=seed, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=seed, check=True)
    (seed / "README.md").write_text("fixture\n")
    subprocess.run(["git", "add", "README.md"], cwd=seed, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=seed, check=True, capture_output=True)
    subprocess.run(["git", "clone", "--bare", seed, remote], check=True, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=seed, check=True)
    subprocess.run(["git", "checkout", "-b", "codex/resume"], cwd=seed, check=True, capture_output=True)
    (seed / "resume.txt").write_text("resume\n")
    subprocess.run(["git", "add", "resume.txt"], cwd=seed, check=True)
    subprocess.run(["git", "commit", "-m", "resume"], cwd=seed, check=True, capture_output=True)
    subprocess.run(["git", "push", "origin", "codex/resume"], cwd=seed, check=True, capture_output=True)
    registry = tmp_path / "repositories.yaml"
    registry.write_text(yaml.safe_dump({"schema_version": 1, "repositories": [{
        "id":"fixture", "github":"example/fixture", "remote_url":str(remote),
        "default_branch":"main", "allowed_branches":["main","codex/resume"],
        "allowed_branch_prefixes":["hermes/agent/"],
        "visibility":"private", "allowed_agents":["agent"]}]}))
    return registry, remote


def test_containment_rejects_traversal_and_symlinks(tmp_path):
    with pytest.raises(HermesError): canonical_child(tmp_path, "..", "escape")
    (tmp_path / "link").symlink_to(tmp_path / "target")
    with pytest.raises(HermesError): canonical_child(tmp_path, "link", "child")
    root_link = tmp_path / "root-link"
    root_link.symlink_to(tmp_path / "target")
    with pytest.raises(HermesError): canonical_child(root_link, "child")


def test_reconcile_entrypoint_does_not_mutate_immutable_bundle_with_bytecode(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("runtime_reconcile.py", "hermes_common.py"):
        shutil.copyfile(SCRIPTS / name, scripts / name)
    result = subprocess.run(
        [sys.executable, str(scripts / "runtime_reconcile.py"), "--help"],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0
    assert not (scripts / "__pycache__").exists()


def test_workspace_modes_identity_and_external_receipt(tmp_path, git_remote):
    registry, _ = git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    detached=workspace_manager.create(registry,root,state,"agent","fixture","read1",False)
    assert detached["mode"]=="detached" and detached["branch"] is None
    assert (state/"receipts/read1.json").is_file()
    assert set(json.loads((root/"agent/read1/.hermes-workspace.json").read_text()))=={"task_id"}
    writable=workspace_manager.create(registry,root,state,"agent","fixture","write1",True)
    assert writable["branch"]=="hermes/agent/write1"
    resumed=workspace_manager.create(registry,root,state,"agent","fixture","resume1",True,"codex/resume")
    assert resumed["mode"]=="resume" and (root/"agent/resume1/resume.txt").is_file()


def test_workspace_identity_accepts_durable_receipt_shape_and_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(workspace_manager, "run", lambda _argv, _cwd: "git@github.com:example/fixture.git")
    workspace_manager._assert_identity(tmp_path, {
        "remote_url": "git@github.com:example/fixture.git",
        "repository": "example/fixture",
    })
    with pytest.raises(HermesError, match="receipt identity is incomplete"):
        workspace_manager._assert_identity(tmp_path, {"remote_url": "git@github.com:example/fixture.git"})


def test_workspace_preserves_dirty_and_unpushed_work(tmp_path, git_remote):
    registry,_=git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    rec=workspace_manager.create(registry,root,state,"agent","fixture","dirty",True)
    workspace=Path(rec["workspace"]); (workspace/"local.txt").write_text("keep")
    result=workspace_manager.cleanup(workspace,state,"dirty")
    assert result["removed"] is False and result["preserve"] and workspace.exists()
    subprocess.run(["git","add","local.txt"],cwd=workspace,check=True)
    subprocess.run(["git","-c","user.name=Fixture","-c","user.email=x@y.invalid","commit","-m","local"],cwd=workspace,check=True,capture_output=True)
    assert workspace_manager.inventory(root,state)[0]["ahead_of_base"]==1


def test_workspace_cleans_only_after_commit_is_remote_reachable(tmp_path, git_remote):
    registry,_=git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    rec=workspace_manager.create(registry,root,state,"agent","fixture","pushed",True)
    workspace=Path(rec["workspace"]); (workspace/"result.txt").write_text("safe\n")
    subprocess.run(["git","add","result.txt"],cwd=workspace,check=True)
    subprocess.run(["git","-c","user.name=Fixture","-c","user.email=x@y.invalid","commit","-m","result"],cwd=workspace,check=True,capture_output=True)
    assert workspace_manager.cleanup(workspace,state,"pushed")["removed"] is False
    subprocess.run(["git","push","-u","origin","HEAD"],cwd=workspace,check=True,capture_output=True)
    facts=workspace_manager.inspect(workspace,rec)
    assert facts["unpushed_commits"]==0 and facts["remote_reachable"] is True
    assert workspace_manager.cleanup(workspace,state,"pushed")["removed"] is True
    assert not workspace.exists()


def test_workspace_preserves_when_remote_branch_disappears(tmp_path, git_remote):
    registry,_=git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    rec=workspace_manager.create(registry,root,state,"agent","fixture","remote-gone",True)
    workspace=Path(rec["workspace"]); (workspace/"result.txt").write_text("safe\n")
    subprocess.run(["git","add","result.txt"],cwd=workspace,check=True)
    subprocess.run(["git","-c","user.name=Fixture","-c","user.email=x@y.invalid","commit","-m","result"],cwd=workspace,check=True,capture_output=True)
    subprocess.run(["git","push","-u","origin","HEAD"],cwd=workspace,check=True,capture_output=True)
    subprocess.run(["git","push","origin","--delete",rec["branch"]],cwd=workspace,check=True,capture_output=True)
    result=workspace_manager.cleanup(workspace,state,"remote-gone")
    assert result["removed"] is False and result["remote_refresh_failed"] and workspace.exists()


def test_workspace_rejects_non_allowlisted_or_implicit_resume(tmp_path, git_remote):
    registry,_=git_remote
    with pytest.raises(HermesError): workspace_manager.create(registry,tmp_path/"w",tmp_path/"s","intruder","fixture","bad0",True)
    with pytest.raises(HermesError): workspace_manager.create(registry,tmp_path/"w",tmp_path/"s","agent","fixture","bad",True,"main")
    with pytest.raises(HermesError): workspace_manager.create(registry,tmp_path/"w",tmp_path/"s","agent","fixture","bad2",True,"codex/unapproved")


def test_writer_lease_fencing_and_idempotent_effects(tmp_path):
    db=writer_lease.connect(tmp_path/"ledger.db")
    epoch=writer_lease.acquire(db,"profile","writer-a",30,now=100)
    first=writer_lease.prepare(db,"profile","writer-a",epoch,"email","send-1","mail","abc",now=101)
    assert first["state"]=="prepared"
    assert writer_lease.prepare(db,"profile","writer-a",epoch,"email","send-1","mail","abc",now=102)["state"]=="prepared"
    with pytest.raises(HermesError): writer_lease.prepare(db,"profile","writer-a",epoch,"email","send-1","mail","different",now=102)
    assert writer_lease.transition(db,"profile","writer-a",epoch,"email","send-1","submitting",now=103)["state"]=="submitting"
    assert writer_lease.transition(db,"profile","writer-a",epoch,"email","send-1","submitted",now=103)["state"]=="submitted"
    with pytest.raises(HermesError): writer_lease.transition(db,"profile","writer-a",epoch,"email","send-1","provider-confirmed",now=104)
    confirmed=writer_lease.transition(db,"profile","writer-a",epoch,"email","send-1","provider-confirmed","provider-42",now=104)
    assert confirmed["provider_reference"]=="provider-42"
    new_epoch=writer_lease.acquire(db,"profile","writer-b",30,now=200)
    assert new_epoch==epoch+1
    with pytest.raises(HermesError): writer_lease.prepare(db,"profile","writer-a",epoch,"email","send-2","mail","x",now=201)


def test_writer_lease_is_exclusive(tmp_path):
    db=writer_lease.connect(tmp_path/"ledger.db"); writer_lease.acquire(db,"p","one",30,now=1)
    with pytest.raises(HermesError): writer_lease.acquire(db,"p","two",30,now=2)
    assert writer_lease.acquire(db,"p","one",30,now=40)==2
    assert writer_lease.release(db,"p","one",2,now=41)==2
    assert writer_lease.acquire(db,"p","two",30,now=41)==3


def test_effect_broker_fences_and_deduplicates_provider_calls(tmp_path):
    db_path=tmp_path/"ledger.db"; db=writer_lease.connect(db_path); epoch=writer_lease.acquire(db,"profile","writer",300)
    request=tmp_path/"request.json"; request.write_text('{"message":"fixture"}')
    plan=tmp_path/"effect.yaml"; plan.write_text(yaml.safe_dump({"schema_version":1,"profile":"profile","action_type":"email","target_alias":"mail","idempotency_key":"send-1","policy_decision":"allowed","request_file":str(request),"request_sha256":__import__("hashlib").sha256(request.read_bytes()).hexdigest()}))
    signature=tmp_path/"effect.sig"; signature.write_bytes(plan.read_bytes()); verifier=executable(tmp_path/"approval-verify",'cmp -s "$1" "$2"\n')
    calls=tmp_path/"calls"
    adapter=executable(tmp_path/"adapter",f'printf "%s\\n" "$1" >> "{calls}"\nif [ "$1" = submit ]; then printf \'{{"provider_reference":"provider-1"}}\'; else printf \'{{"confirmed":true}}\'; fi\n')
    assert effect_broker.execute(db_path,"writer",epoch,plan,signature,verifier,adapter,tmp_path/"broker-state")["state"]=="provider-confirmed"
    assert effect_broker.execute(db_path,"writer",epoch,plan,signature,verifier,adapter,tmp_path/"broker-state")["state"]=="provider-confirmed"
    assert calls.read_text().splitlines()==["submit","lookup"]


def test_effect_broker_recovers_inflight_by_lookup_without_resubmit(tmp_path):
    db_path=tmp_path/"ledger.db"; db=writer_lease.connect(db_path); epoch=writer_lease.acquire(db,"profile","writer",300)
    request=tmp_path/"request.json"; request.write_text('{}'); digest=__import__("hashlib").sha256(request.read_bytes()).hexdigest()
    plan=tmp_path/"effect.yaml"; plan.write_text(yaml.safe_dump({"schema_version":1,"profile":"profile","action_type":"email","target_alias":"mail","idempotency_key":"send-2","policy_decision":"allowed","request_file":str(request),"request_sha256":digest}))
    signature=tmp_path/"effect.sig"; signature.write_bytes(plan.read_bytes()); verifier=executable(tmp_path/"verify",'cmp -s "$1" "$2"\n'); calls=tmp_path/"calls"
    writer_lease.prepare(db,"profile","writer",epoch,"email","send-2","mail",digest)
    writer_lease.transition(db,"profile","writer",epoch,"email","send-2","submitting")
    with effect_broker.approved_copy(plan,signature,verifier,tmp_path/"broker-state"): pass
    plan.unlink(); signature.unlink(); request.unlink()
    adapter=executable(tmp_path/"adapter",f'printf "%s\\n" "$1" >> "{calls}"\nprintf \'{{"confirmed":true,"provider_reference":"provider-2"}}\'\n')
    result=effect_broker.recover(db_path,"writer",epoch,"profile","email","send-2",verifier,adapter,tmp_path/"broker-state")
    assert result["state"]=="provider-confirmed" and calls.read_text().splitlines()==["lookup"]


def test_effect_broker_authoritative_not_found_retries_idempotently(tmp_path):
    db_path=tmp_path/"ledger.db"; db=writer_lease.connect(db_path); epoch=writer_lease.acquire(db,"profile","writer",300)
    request=tmp_path/"request.json"; request.write_text('{}'); digest=__import__("hashlib").sha256(request.read_bytes()).hexdigest()
    plan=tmp_path/"effect.yaml"; plan.write_text(yaml.safe_dump({"schema_version":1,"profile":"profile","action_type":"email","target_alias":"mail","idempotency_key":"send-3","policy_decision":"allowed","request_file":str(request),"request_sha256":digest}))
    signature=tmp_path/"effect.sig"; signature.write_bytes(plan.read_bytes()); verifier=executable(tmp_path/"verify",'cmp -s "$1" "$2"\n'); calls=tmp_path/"calls"
    with effect_broker.approved_copy(plan,signature,verifier,tmp_path/"broker-state"): pass
    writer_lease.prepare(db,"profile","writer",epoch,"email","send-3","mail",digest); writer_lease.transition(db,"profile","writer",epoch,"email","send-3","submitting")
    adapter=executable(tmp_path/"adapter",f'printf "%s\\n" "$1" >> "{calls}"\ncount=$(wc -l < "{calls}" | tr -d " ")\nif [ "$1" = lookup ] && [ "$count" = 1 ]; then printf \'{{"not_found":true}}\'; elif [ "$1" = submit ]; then printf \'{{"provider_reference":"provider-3"}}\'; else printf \'{{"confirmed":true}}\'; fi\n')
    result=effect_broker.recover(db_path,"writer",epoch,"profile","email","send-3",verifier,adapter,tmp_path/"broker-state")
    assert result["state"]=="provider-confirmed" and calls.read_text().splitlines()==["lookup","submit","lookup"]


def test_effect_socket_rejects_wrong_peer_before_credentials(tmp_path):
    with pytest.raises(HermesError): effect_socket.handle({"plan":"x","signature":"y"},501,502,"profile",tmp_path/"db",tmp_path/"verify",tmp_path/"adapter",tmp_path/"state")


def test_systemd_units_keep_profile_users_and_credentials_separate():
    systemd=SCRIPTS.parent/"systemd"
    gateway=(systemd/"hermes-gateway@.service").read_text()
    broker=(systemd/"hermes-effect-broker@.service").read_text()
    backup=(systemd/"hermes-profile-backup@.service").read_text()
    assert "User=hermes-frontdoor-%i" in gateway
    assert "LoadCredential=frontdoor.env:/etc/hermes/credentials/%i.frontdoor.env" in gateway
    assert "CODEX_HOME=" not in gateway and ".effect.env" not in gateway
    assert "User=hermes-broker-%i" in broker
    assert "LoadCredential=effect.env:/etc/hermes/credentials/%i.effect.env" in broker
    assert ".frontdoor.env" not in broker
    assert "User=hermes-backup-%i" in backup and "Group=hermes-backup-%i" in backup


def bundle_fixture(tmp_path, revision=1):
    payload=tmp_path/f"payload-{revision}"; payload.write_text(f"payload {revision}")
    signer=executable(tmp_path/"sign",'cp "$1" "$2"\n')
    verifier=executable(tmp_path/"verify",'cmp -s "$1" "$2"\n')
    spec=tmp_path/f"spec-{revision}.yaml"
    spec.write_text(yaml.safe_dump({"profile":"profile","version":"4.0.0-rc.3","revision":revision,"core_commit":"a"*40,"control_commit":"b"*40,"files":[{"source":str(payload),"destination":"bin/payload","executable":True}]}))
    return render_agent_bundle.render(spec,tmp_path/"bundles",signer),verifier


def test_signed_bundle_and_atomic_reconcile_with_replay_protection(tmp_path):
    bundle,verifier=bundle_fixture(tmp_path,1); health=executable(tmp_path/"health","test -f bin/payload\n")
    state=runtime_reconcile.reconcile(bundle,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(health)])
    assert state["writer_enablement"]=="requires-supervisor"
    current=tmp_path/"deploy/profile/current"; assert current.is_symlink()
    with pytest.raises(HermesError): runtime_reconcile.reconcile(bundle,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(health)])


def test_reconcile_rolls_back_before_writer_enablement(tmp_path):
    first,verifier=bundle_fixture(tmp_path,1); good=executable(tmp_path/"good","exit 0\n")
    runtime_reconcile.reconcile(first,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    old=(tmp_path/"deploy/profile/current").resolve()
    second,_=bundle_fixture(tmp_path,2); bad=executable(tmp_path/"bad","exit 1\n")
    with pytest.raises(HermesError): runtime_reconcile.reconcile(second,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(bad)])
    assert (tmp_path/"deploy/profile/current").resolve()==old


def test_reconcile_rolls_back_when_health_cannot_start(tmp_path):
    first,verifier=bundle_fixture(tmp_path,1); good=executable(tmp_path/"good","exit 0\n")
    runtime_reconcile.reconcile(first,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    old=(tmp_path/"deploy/profile/current").resolve(); second,_=bundle_fixture(tmp_path,2)
    with pytest.raises(HermesError): runtime_reconcile.reconcile(second,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(tmp_path/"missing-health")])
    assert (tmp_path/"deploy/profile/current").resolve()==old


def test_post_effect_rollback_requires_generation_bound_supervision(tmp_path):
    first,verifier=bundle_fixture(tmp_path,1); good=executable(tmp_path/"good","exit 0\n")
    runtime_reconcile.reconcile(first,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    second,_=bundle_fixture(tmp_path,2); runtime_reconcile.reconcile(second,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    runtime_reconcile.mark_writer_enabled(tmp_path/"state","profile","4.0.0-rc.3",2)
    with pytest.raises(HermesError): runtime_reconcile.supervised_rollback(tmp_path/"deploy",tmp_path/"state","profile","",verifier)
    state=runtime_reconcile.supervised_rollback(tmp_path/"deploy",tmp_path/"state","profile","profile:4.0.0-rc.3:r2",verifier)
    assert state["writer_enablement"]=="disabled-pending-reconciliation"


def test_supervised_rollback_reverifies_previous_generation(tmp_path):
    first,verifier=bundle_fixture(tmp_path,1); good=executable(tmp_path/"good","exit 0\n")
    runtime_reconcile.reconcile(first,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    second,_=bundle_fixture(tmp_path,2); runtime_reconcile.reconcile(second,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    previous=tmp_path/"deploy/profile/releases/4.0.0-rc.3-r1/bin/payload"; previous.chmod(0o755); previous.write_text("tampered")
    with pytest.raises(HermesError): runtime_reconcile.supervised_rollback(tmp_path/"deploy",tmp_path/"state","profile","",verifier)


def test_reconcile_recovers_durable_pending_activation_after_crash(tmp_path):
    first,verifier=bundle_fixture(tmp_path,1); good=executable(tmp_path/"good","exit 0\n")
    active=runtime_reconcile.reconcile(first,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    second,_=bundle_fixture(tmp_path,2); candidate=tmp_path/"deploy/profile/releases/4.0.0-rc.3-r2"; shutil.copytree(second,candidate)
    current=tmp_path/"deploy/profile/current"; current.unlink(); current.symlink_to(candidate)
    pending={"phase":"activating","profile":"profile","version":"4.0.0-rc.3","revision":2,"candidate":str(candidate),"previous":active["bundle"],"prior_state":active,"intent_recorded_at":1}
    state_file=tmp_path/"state/reconcile/profile.json"; state_file.write_text(json.dumps(pending))
    third,_=bundle_fixture(tmp_path,3)
    result=runtime_reconcile.reconcile(third,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    assert result["revision"]==3 and result["previous"]==active["bundle"] and not candidate.exists()


def test_reconcile_completes_durable_pending_supervised_rollback(tmp_path):
    first,verifier=bundle_fixture(tmp_path,1); good=executable(tmp_path/"good","exit 0\n")
    one=runtime_reconcile.reconcile(first,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    second,_=bundle_fixture(tmp_path,2); two=runtime_reconcile.reconcile(second,tmp_path/"deploy","profile",tmp_path/"state",verifier,[str(good)])
    result={**two,"phase":"rolled-back","bundle":one["bundle"],"rolled_back_from":two["bundle"],"writer_enablement":"disabled-pending-reconciliation"}
    pending={"phase":"rolling-back","profile":"profile","target":one["bundle"],"from":two["bundle"],"result_state":result,"intent_recorded_at":1}
    state_file=tmp_path/"state/reconcile/profile.json"; state_file.write_text(json.dumps(pending))
    recovered=runtime_reconcile.recover_pending(state_file,tmp_path/"deploy/profile",tmp_path/"deploy/profile/releases","profile",verifier)
    assert recovered["phase"]=="rolled-back" and (tmp_path/"deploy/profile/current").resolve()==Path(one["bundle"])


def test_bundle_rejects_unsigned_symlink_and_tampering(tmp_path):
    payload=tmp_path/"payload"; payload.write_text("x"); link=tmp_path/"link"; link.symlink_to(payload)
    spec=tmp_path/"spec.yaml"; spec.write_text(yaml.safe_dump({"profile":"p","version":"1.0.0","revision":1,"core_commit":"a"*40,"control_commit":"b"*40,"files":[{"source":str(link),"destination":"x"}]}))
    with pytest.raises(HermesError): render_agent_bundle.render(spec,tmp_path/"out",executable(tmp_path/"sign","cp \"$1\" \"$2\"\n"))
    bundle,verifier=bundle_fixture(tmp_path,1); (bundle/"bin/payload").chmod(0o755); (bundle/"bin/payload").write_text("tampered")
    with pytest.raises(HermesError): runtime_reconcile.verify(bundle,verifier)


def test_bundle_verifier_rejects_extra_symlink(tmp_path):
    bundle,verifier=bundle_fixture(tmp_path,1)
    bundle.chmod(0o755)
    (bundle/"escape").symlink_to(tmp_path/"payload-1")
    with pytest.raises(HermesError): runtime_reconcile.verify(bundle,verifier)


def test_profile_backup_restore_and_checksum(tmp_path):
    source=tmp_path/"profile"; source.mkdir(); (source/"memory.db").write_text("state")
    copy=executable(tmp_path/"copy",'cp "$1" "$2"\n'); snapshot=executable(tmp_path/"snapshot",'cp -R "$1"/. "$2"/\n'); archive=tmp_path/"backup.age"
    manifest=profile_backup.backup("profile",source,archive,copy,snapshot)
    restored=tmp_path/"restored"; result=profile_backup.restore(archive,archive.with_suffix(".age.json"),restored,copy)
    assert result["rehearsal"] and (restored/"memory.db").read_text()=="state"
    archive.write_text("bad")
    with pytest.raises(HermesError): profile_backup.restore(archive,archive.with_suffix(".age.json"),tmp_path/"other",copy)


def test_memory_validation_routes_and_rejects_private_material(tmp_path):
    base={"schema_version":1,"kind":"procedure_improvement","agent":"a","source_task":"t","observed_at":"2026-07-16T12:00:00Z","scope":"core","sensitivity":"internal","confidence":.8,"proposed_destination":"multiplai-core","summary":"Generic validation improvement"}
    path=tmp_path/"candidate.yaml"; path.write_text(yaml.safe_dump(base))
    assert memory_review.review(path)=={"accepted":True,"route":"multiplai-core","auto_merge":False,"requires_pr_review":True}
    base["summary"]="Contains raw transcript"; path.write_text(yaml.safe_dump(base))
    with pytest.raises(HermesError): memory_review.review(path)


def test_memory_validation_rejects_extra_or_mistyped_fields(tmp_path):
    base={"schema_version":1,"kind":"personal_policy","agent":"a","source_task":"t","observed_at":"2026-07-16T12:00:00Z","scope":"profile","sensitivity":"confidential","confidence":.8,"proposed_destination":"example-personal","summary":"Owner preference"}
    path=tmp_path/"candidate.yaml"
    path.write_text(yaml.safe_dump({**base,"raw_content":"must not cross the boundary"}))
    with pytest.raises(HermesError): memory_review.review(path)
    base["confidence"]="high"; path.write_text(yaml.safe_dump(base))
    with pytest.raises(HermesError): memory_review.review(path)
    base["confidence"]=.8; base["proposed_destination"]="multiplai-core"; path.write_text(yaml.safe_dump(base))
    with pytest.raises(HermesError): memory_review.review(path)


@pytest.mark.parametrize("destination", ["example-operations", "example-client", "example/team"])
def test_entity_memory_routes_only_to_an_operating_repository(tmp_path, destination):
    candidate={"schema_version":1,"kind":"entity_fact","agent":"a","source_task":"t","observed_at":"2026-07-16T12:00:00Z","scope":"entity","sensitivity":"internal","confidence":.9,"proposed_destination":destination,"summary":"Reviewed entity fact"}
    path=tmp_path/"candidate.yaml"; path.write_text(yaml.safe_dump(candidate))
    routes = tmp_path / "routes.yaml"
    routes.write_text(yaml.safe_dump({"schema_version": 1, "routes": {"entity_fact": [destination]}}))
    with pytest.raises(HermesError, match="configure"):
        memory_review.review(path)
    assert memory_review.review(path, routes)["route"] == destination
    routes.write_text(yaml.safe_dump({"schema_version": 1, "routes": {"entity_fact": [destination], "generic_tool": [destination]}}))
    with pytest.raises(HermesError, match="overlap"):
        memory_review.review(path, routes)


def test_task_runner_scrubs_environment_and_uses_dedicated_homes(tmp_path, git_remote, monkeypatch):
    registry,_=git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    receipt=workspace_manager.create(registry,root,state,"agent","fixture","task1",False)
    workspace=Path(receipt["workspace"]); output=tmp_path/"env.json"
    fake=executable(tmp_path/"fakecodex", f'python3 -c \'import json,os;open("{output}","w").write(json.dumps(dict(os.environ)))\'\n')
    executor=tmp_path/"executor.yaml"; executor.write_text(yaml.safe_dump({"id":"codex","command":str(fake),"environment_allowlist":["PATH","LANG"],"fallback":"prohibited","required_user_template":pwd.getpwuid(os.geteuid()).pw_name}))
    verifier=executable(tmp_path/"verifycore",'test -d "$1/.git"\n')
    contract=tmp_path/"task.yaml"; contract.write_text(yaml.safe_dump({"schema_version":1,"task_id":"task1","profile":"profile","agent":"agent","repository":"example/fixture","base_sha":receipt["base_sha"],"branch":None,"executor":"codex","instruction":"fixture task","timeout_seconds":10,"credential_aliases":[],"validation":[],"external_actions":[],"recovery_state":"clean"}))
    monkeypatch.setenv("SHOULD_NOT_LEAK","secret")
    result=task_runner.run_task(contract,workspace,state/"receipts/task1.json",executor,state,tmp_path/"runtime",core_verifier=verifier)
    child=json.loads(output.read_text()); assert result["status"]=="succeeded" and "SHOULD_NOT_LEAK" not in child
    assert child["HOME"].startswith(str(tmp_path/"runtime/homes/profile/task1"))
    assert child["CODEX_HOME"]!=child["HOME"] and child["GH_CONFIG_DIR"]!=child["HOME"]


def test_task_runner_rejects_fallback_or_identity_mismatch(tmp_path):
    contract=tmp_path/"task.yaml"; contract.write_text("task_id: x\nprofile: p\nexecutor: codex\n")
    executor=tmp_path/"executor.yaml"; executor.write_text("id: codex\ncommand: true\nfallback: allowed\n")
    receipt=tmp_path/"receipt.json"; receipt.write_text(json.dumps({"task_id":"x","workspace":str(tmp_path)}))
    with pytest.raises(HermesError): task_runner.run_task(contract,tmp_path,receipt,executor,tmp_path,tmp_path/"r")
    assert json.loads((tmp_path/"task-receipts/x.json").read_text())["status"]=="blocked"


def test_task_runner_timeout_writes_terminal_receipt(tmp_path, git_remote):
    registry,_=git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    receipt=workspace_manager.create(registry,root,state,"agent","fixture","slow",False); workspace=Path(receipt["workspace"])
    fake=executable(tmp_path/"slowcodex","sleep 5\n"); executor=tmp_path/"executor.yaml"; executor.write_text(yaml.safe_dump({"id":"codex","command":str(fake),"environment_allowlist":["PATH"],"fallback":"prohibited","required_user_template":pwd.getpwuid(os.geteuid()).pw_name}))
    contract=tmp_path/"task.yaml"; contract.write_text(yaml.safe_dump({"schema_version":1,"task_id":"slow","profile":"p","agent":"agent","repository":"example/fixture","base_sha":receipt["base_sha"],"branch":None,"executor":"codex","instruction":"wait","timeout_seconds":1,"credential_aliases":[],"validation":[],"external_actions":[],"recovery_state":"clean"}))
    verifier=executable(tmp_path/"verifycore",'test -d "$1/.git"\n')
    result=task_runner.run_task(contract,workspace,state/"receipts/slow.json",executor,state,tmp_path/"runtime",core_verifier=verifier)
    assert result["status"]=="timed-out" and json.loads((state/"task-receipts/slow.json").read_text())["status"]=="timed-out"


def test_task_runner_cancellation_writes_terminal_receipt(tmp_path, git_remote):
    registry,_=git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    receipt=workspace_manager.create(registry,root,state,"agent","fixture","cancel",False); workspace=Path(receipt["workspace"])
    fake=executable(tmp_path/"slowcodex","sleep 5\n"); verifier=executable(tmp_path/"verifycore",'test -d "$1/.git"\n')
    executor=tmp_path/"executor.yaml"; executor.write_text(yaml.safe_dump({"id":"codex","command":str(fake),"environment_allowlist":["PATH"],"fallback":"prohibited","required_user_template":pwd.getpwuid(os.geteuid()).pw_name}))
    contract=tmp_path/"task.yaml"; contract.write_text(yaml.safe_dump({"schema_version":1,"task_id":"cancel","profile":"p","agent":"agent","repository":"example/fixture","base_sha":receipt["base_sha"],"branch":None,"executor":"codex","instruction":"wait","timeout_seconds":10,"credential_aliases":[],"validation":[],"external_actions":[],"recovery_state":"clean"}))
    cancel=tmp_path/"cancel.request"; cancel.write_text("cancel\n")
    result=task_runner.run_task(contract,workspace,state/"receipts/cancel.json",executor,state,tmp_path/"runtime",cancel_file=cancel,core_verifier=verifier)
    assert result["status"]=="cancelled"
    assert json.loads((state/"task-receipts/cancel.json").read_text())["status"]=="cancelled"


def test_credential_broker_is_alias_scoped(tmp_path):
    broker=executable(tmp_path/"broker",'test "$1" = resolve-task\ntest "$2" = p\ntest "$3" = t\nprintf \'{"mail":"fixture"}\'\n')
    executor={"environment_allowlist":["PATH"]}
    env=task_runner.isolated_env(tmp_path/"runtime","p","t",executor,broker,["mail"])
    assert env["HERMES_CREDENTIAL_MAIL"]=="fixture"
    with pytest.raises(HermesError): task_runner.isolated_env(tmp_path/"runtime","p","u",executor,broker,["calendar"])


def test_codex_executor_maps_oauth_to_private_auth_file():
    executor=yaml.safe_load((SCRIPTS.parent/"executors/codex.yaml").read_text())
    assert executor["credential_files"]=={"codex_oauth":"auth.json"}
    assert "credential_environment" not in executor


def test_credential_file_mapping_rejects_overlap_and_traversal(tmp_path):
    broker=executable(tmp_path/"broker",'exit 1\n')
    executor={"environment_allowlist":["PATH"],"credential_environment":{"same":"TOKEN"},"credential_files":{"same":"auth.json"}}
    with pytest.raises(HermesError): task_runner.isolated_env(tmp_path/"runtime","p","t",executor,broker,["same"])
    with pytest.raises(HermesError): task_runner.credential_file_mapping({"credential_files":{"codex_oauth":"../auth.json"}})


def test_task_runner_persists_refreshed_oauth_and_removes_task_copy(tmp_path, git_remote):
    registry,_=git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    receipt=workspace_manager.create(registry,root,state,"agent","fixture","oauth",False); workspace=Path(receipt["workspace"])
    stored=tmp_path/"stored-auth.json"; stored.write_text('{"tokens":{"access_token":"initial"}}')
    broker=executable(tmp_path/"broker",f'''case "$1" in
materialize-task) cp "{stored}" "$5"; chmod 600 "$5" ;;
persist-task) cp "$5" "{stored}" ;;
*) exit 1 ;;
esac
''')
    fake=executable(tmp_path/"fakecodex",'''printf '%s' '{"tokens":{"access_token":"refreshed"}}' > "$CODEX_HOME/auth.json"
chmod 600 "$CODEX_HOME/auth.json"
''')
    executor=tmp_path/"executor.yaml"; executor.write_text(yaml.safe_dump({"id":"codex","command":str(fake),"environment_allowlist":["PATH"],"credential_files":{"codex_oauth":"auth.json"},"fallback":"prohibited","required_user_template":pwd.getpwuid(os.geteuid()).pw_name}))
    contract=tmp_path/"task.yaml"; contract.write_text(yaml.safe_dump({"schema_version":1,"task_id":"oauth","profile":"p","agent":"agent","repository":"example/fixture","base_sha":receipt["base_sha"],"branch":None,"executor":"codex","instruction":"refresh","timeout_seconds":10,"credential_aliases":["codex_oauth"],"validation":[],"external_actions":[],"recovery_state":"clean"}))
    verifier=executable(tmp_path/"verifycore",'test -d "$1/.git"\n')
    result=task_runner.run_task(contract,workspace,state/"receipts/oauth.json",executor,state,tmp_path/"runtime",credential_broker=broker,core_verifier=verifier)
    assert result["status"]=="succeeded" and result["credential_persistence"]=="persisted"
    assert json.loads(stored.read_text())["tokens"]["access_token"]=="refreshed"
    assert not (tmp_path/"runtime/codex/p/oauth/auth.json").exists()
    assert "initial" not in json.dumps(result) and "refreshed" not in json.dumps(result)


def test_task_runner_preserves_private_oauth_copy_when_persistence_fails(tmp_path, git_remote):
    registry,_=git_remote; root=tmp_path/"work"; state=tmp_path/"state"
    receipt=workspace_manager.create(registry,root,state,"agent","fixture","oauth-fail",False); workspace=Path(receipt["workspace"])
    seed=tmp_path/"seed-auth.json"; seed.write_text('{"tokens":{"access_token":"initial"}}')
    broker=executable(tmp_path/"broker",f'''if [ "$1" = materialize-task ]; then cp "{seed}" "$5"; chmod 600 "$5"; exit 0; fi
exit 1
''')
    fake=executable(tmp_path/"fakecodex",'''printf '%s' '{"tokens":{"access_token":"token-only-in-file"}}' > "$CODEX_HOME/auth.json"
chmod 600 "$CODEX_HOME/auth.json"
''')
    executor=tmp_path/"executor.yaml"; executor.write_text(yaml.safe_dump({"id":"codex","command":str(fake),"environment_allowlist":["PATH"],"credential_files":{"codex_oauth":"auth.json"},"fallback":"prohibited","required_user_template":pwd.getpwuid(os.geteuid()).pw_name}))
    contract=tmp_path/"task.yaml"; contract.write_text(yaml.safe_dump({"schema_version":1,"task_id":"oauth-fail","profile":"p","agent":"agent","repository":"example/fixture","base_sha":receipt["base_sha"],"branch":None,"executor":"codex","instruction":"refresh","timeout_seconds":10,"credential_aliases":["codex_oauth"],"validation":[],"external_actions":[],"recovery_state":"clean"}))
    verifier=executable(tmp_path/"verifycore",'test -d "$1/.git"\n')
    result=task_runner.run_task(contract,workspace,state/"receipts/oauth-fail.json",executor,state,tmp_path/"runtime",credential_broker=broker,core_verifier=verifier)
    recovery=tmp_path/"runtime/codex/p/oauth-fail/auth.json"
    assert result["status"]=="error" and result["credential_persistence"]=="failed"
    assert result["recovery_state"]=="blocked" and recovery.is_file()
    assert json.loads(recovery.read_text())["tokens"]["access_token"]=="token-only-in-file"
    assert "token-only-in-file" not in json.dumps(result)


def test_materialized_oauth_rejects_symlink(tmp_path):
    target=tmp_path/"target"; target.write_text("secret")
    broker=executable(tmp_path/"broker",f'ln -s "{target}" "$5"\n')
    with pytest.raises(HermesError):
        task_runner.materialize_credential_files(tmp_path/"runtime","p","t",{"credential_files":{"codex_oauth":"auth.json"}},broker,["codex_oauth"])
    assert not (tmp_path/"runtime/codex/p/t/auth.json").exists()


def test_task_manifest_keeps_effecting_credentials_out_of_codex():
    task={"schema_version":1,"task_id":"t","profile":"p","agent":"a","repository":"example/repo","base_sha":"a"*40,"branch":None,"executor":"codex","instruction":"prepare","timeout_seconds":10,"credential_aliases":["mail"],"validation":[],"external_actions":[{"action_type":"email","target_alias":"mail","idempotency_key":"send-1","policy_decision":"approval-required"}],"recovery_state":"clean"}
    with pytest.raises(HermesError): task_runner.validate_contract(task)


@pytest.mark.parametrize('destination', ['../private', 'example/..', '/absolute', 'https://example.com', '*'])
def test_memory_routing_rejects_paths_and_wildcards(tmp_path, destination):
    policy = tmp_path / 'routes.yaml'
    policy.write_text(yaml.safe_dump({'schema_version': 1, 'routes': {'entity_fact': [destination]}}))
    with pytest.raises(HermesError, match='explicit repository'):
        memory_review.load_routes(policy)


def test_private_routes_cannot_use_core_when_shared_routes_are_omitted(tmp_path):
    policy = tmp_path / 'routes.yaml'
    policy.write_text(yaml.safe_dump({'schema_version': 1, 'routes': {'entity_fact': ['multiplai-core']}}))
    with pytest.raises(HermesError, match='overlap'):
        memory_review.load_routes(policy)


@pytest.mark.parametrize('routes', [
    {'entity_fact': ['multiplai-ai/multiplai-core']},
    {'personal_policy': ['Example/Private'], 'entity_fact': ['example/private']},
    {'personal_policy': ['private'], 'entity_fact': ['example/private']},
])
def test_memory_routes_reject_qualified_and_case_aliases(tmp_path, routes):
    policy = tmp_path / 'routes.yaml'
    policy.write_text(yaml.safe_dump({'schema_version': 1, 'routes': routes}))
    with pytest.raises(HermesError, match='overlap'):
        memory_review.load_routes(policy)
