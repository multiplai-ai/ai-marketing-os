#!/usr/bin/env python3
"""Execute one approved external effect behind the writer fence and ledger."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

import yaml

from hermes_common import HermesError, canonical_child, ensure_private_dir, fsync_dir, require_id, sha256_file
import writer_lease


REQUIRED={"schema_version","profile","action_type","target_alias","idempotency_key","policy_decision","request_file","request_sha256"}


def require_broker_owned(path: Path, directory: bool = False) -> None:
    if path.is_symlink() or path.resolve()!=path.absolute(): raise HermesError("broker state path is unsafe")
    info=path.stat()
    expected=stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if not expected or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)&0o077: raise HermesError("broker state must be private and broker-owned")


def load_plan(path: Path, request_path: Path | None = None) -> dict:
    plan=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(plan,dict) or set(plan)!=REQUIRED or plan.get("schema_version")!=1 or plan.get("policy_decision")!="allowed":
        raise HermesError("external effect is not explicitly approved")
    for key in ("profile","action_type","target_alias","idempotency_key"): require_id(plan.get(key,""),key.replace("_"," "))
    request=request_path or Path(plan.get("request_file", ""))
    digest=plan.get("request_sha256")
    if request.is_symlink() or not request.is_file() or not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest) or sha256_file(request)!=digest:
        raise HermesError("external effect request digest mismatch")
    return plan


@contextmanager
def approved_copy(plan_path: Path, signature: Path, verifier: Path, state_root: Path):
    """Persist signed inputs in broker-owned storage until terminal recovery."""
    ensure_private_dir(state_root)
    require_broker_owned(state_root,directory=True)
    staging=Path(tempfile.mkdtemp(prefix=".effect-",dir=state_root))
    try:
        staged_plan=staging/"plan.yaml"; staged_sig=staging/"plan.sig"
        staged_plan.write_bytes(plan_path.read_bytes()); staged_sig.write_bytes(signature.read_bytes())
        os.chmod(staged_plan,0o400); os.chmod(staged_sig,0o400)
        checked=subprocess.run([str(verifier),str(staged_plan),str(staged_sig)],text=True,capture_output=True,check=False,env={"PATH":os.environ.get("PATH","")},timeout=15)
        if checked.returncode: raise HermesError("external effect approval signature is invalid")
        unsigned=yaml.safe_load(staged_plan.read_text(encoding="utf-8")) or {}
        for key in ("profile","action_type","idempotency_key"): require_id(unsigned.get(key,""),key.replace("_"," "))
        profile_dir=canonical_child(state_root,unsigned["profile"]); ensure_private_dir(profile_dir)
        action_dir=canonical_child(profile_dir,unsigned["action_type"]); ensure_private_dir(action_dir)
        final=canonical_child(action_dir,unsigned["idempotency_key"])
        persisted_plan=final/"plan.yaml"; persisted_sig=final/"plan.sig"; persisted_request=final/"request.bin"
        if final.exists():
            require_broker_owned(final,directory=True)
            for path in (persisted_plan,persisted_sig,persisted_request): require_broker_owned(path)
            os.chmod(staging,0o700)
            for item in staging.iterdir(): os.chmod(item,0o600)
            shutil.rmtree(staging)
            checked=subprocess.run([str(verifier),str(persisted_plan),str(persisted_sig)],text=True,capture_output=True,check=False,env={"PATH":os.environ.get("PATH","")},timeout=15)
            if checked.returncode: raise HermesError("persisted effect approval signature is invalid")
            persisted=load_plan(persisted_plan,persisted_request)
            if persisted!=unsigned: raise HermesError("persisted effect approval conflicts with request")
            yield persisted,persisted_plan,persisted_request
            return
        request=Path(unsigned.get("request_file", ""))
        if request.is_symlink() or not request.is_file(): raise HermesError("external effect request is unsafe")
        staged_request=staging/"request.bin"; staged_request.write_bytes(request.read_bytes()); os.chmod(staged_request,0o400)
        plan=load_plan(staged_plan,staged_request)
        os.replace(staging,final); os.chmod(final,0o500); fsync_dir(final.parent)
        checked=subprocess.run([str(verifier),str(persisted_plan),str(persisted_sig)],text=True,capture_output=True,check=False,env={"PATH":os.environ.get("PATH","")},timeout=15)
        if checked.returncode: raise HermesError("persisted effect approval signature is invalid")
        persisted=load_plan(persisted_plan,persisted_request)
        if persisted!=plan: raise HermesError("persisted effect approval conflicts with request")
        yield persisted,persisted_plan,persisted_request
    except Exception:
        if staging.exists():
            os.chmod(staging,0o700)
            for item in staging.iterdir(): os.chmod(item,0o600)
            shutil.rmtree(staging,ignore_errors=True)
        raise


def adapter_call(adapter: Path, mode: str, plan_path: Path, request_path: Path, plan: dict) -> dict:
    env={"PATH":os.environ.get("PATH","")}
    if "CREDENTIALS_DIRECTORY" in os.environ: env["CREDENTIALS_DIRECTORY"]=os.environ["CREDENTIALS_DIRECTORY"]
    try:
        result=subprocess.run(
            [str(adapter),mode,str(plan_path),str(request_path),plan["idempotency_key"],plan["target_alias"]],
            text=True,capture_output=True,check=False,env=env,timeout=30,
        )
    except subprocess.TimeoutExpired as exc: raise HermesError(f"provider adapter {mode} timed out") from exc
    if result.returncode: raise HermesError(f"provider adapter {mode} failed")
    try: value=json.loads(result.stdout)
    except json.JSONDecodeError as exc: raise HermesError("provider adapter returned invalid receipt") from exc
    if not isinstance(value,dict): raise HermesError("provider adapter returned invalid receipt")
    return value


def execute(db_path: Path, holder: str, epoch: int, plan_path: Path, signature: Path,
            approval_verifier: Path, adapter: Path, state_root: Path) -> dict:
  with approved_copy(plan_path,signature,approval_verifier,state_root) as (plan,staged_plan,staged_request):
    db=writer_lease.connect(db_path)
    effect=writer_lease.prepare(db,plan["profile"],holder,epoch,plan["action_type"],plan["idempotency_key"],plan["target_alias"],plan["request_sha256"])
    if effect["state"]=="provider-confirmed": return effect
    if effect["state"]=="failed": raise HermesError("external effect is terminally failed")
    if effect["state"]=="prepared":
        effect=writer_lease.transition(db,plan["profile"],holder,epoch,plan["action_type"],plan["idempotency_key"],"submitting")
        writer_lease.renew(db,plan["profile"],holder,epoch,60)
        submitted=adapter_call(adapter,"submit",staged_plan,staged_request,plan)
        writer_lease.renew(db,plan["profile"],holder,epoch,60)
        reference=submitted.get("provider_reference")
        if not isinstance(reference,str) or not reference: raise HermesError("provider submission lacks reference")
        effect=writer_lease.transition(
            db,plan["profile"],holder,epoch,plan["action_type"],
            plan["idempotency_key"],"submitted",reference,
        )
    elif effect["state"]=="submitting":
        writer_lease.renew(db,plan["profile"],holder,epoch,60)
        recovery=adapter_call(adapter,"lookup",staged_plan,staged_request,plan)
        writer_lease.renew(db,plan["profile"],holder,epoch,60)
        if recovery.get("confirmed") is True:
            reference=recovery.get("provider_reference")
            if not isinstance(reference,str) or not reference: raise HermesError("provider confirmation lacks reference")
            return writer_lease.transition(db,plan["profile"],holder,epoch,plan["action_type"],plan["idempotency_key"],"provider-confirmed",reference)
        if recovery.get("not_found") is not True: return effect
        writer_lease.renew(db,plan["profile"],holder,epoch,60)
        submitted=adapter_call(adapter,"submit",staged_plan,staged_request,plan)
        writer_lease.renew(db,plan["profile"],holder,epoch,60)
        reference=submitted.get("provider_reference")
        if not isinstance(reference,str) or not reference: raise HermesError("provider submission lacks reference")
        effect=writer_lease.transition(db,plan["profile"],holder,epoch,plan["action_type"],plan["idempotency_key"],"submitted",reference)
    writer_lease.renew(db,plan["profile"],holder,epoch,60)
    confirmation=adapter_call(adapter,"lookup",staged_plan,staged_request,plan)
    writer_lease.renew(db,plan["profile"],holder,epoch,60)
    if confirmation.get("confirmed") is not True: return effect
    reference=effect.get("provider_reference") or confirmation.get("provider_reference")
    if not isinstance(reference,str) or not reference: raise HermesError("provider confirmation lacks reference")
    return writer_lease.transition(
        db,plan["profile"],holder,epoch,plan["action_type"],
        plan["idempotency_key"],"provider-confirmed",reference,
    )


def recover(db_path: Path, holder: str, epoch: int, profile: str, action_type: str,
            idempotency_key: str, approval_verifier: Path, adapter: Path,
            state_root: Path) -> dict:
    final=canonical_child(state_root,require_id(profile,"profile"),require_id(action_type,"action type"),require_id(idempotency_key,"idempotency key"),must_exist=True)
    return execute(db_path,holder,epoch,final/"plan.yaml",final/"plan.sig",approval_verifier,adapter,state_root)


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--db",type=Path,required=True); p.add_argument("--holder",required=True); p.add_argument("--epoch",type=int,required=True); p.add_argument("--plan",type=Path,required=True); p.add_argument("--signature",type=Path,required=True); p.add_argument("--approval-verifier",type=Path,required=True); p.add_argument("--adapter",type=Path,required=True); p.add_argument("--state-root",type=Path,required=True); a=p.parse_args()
    try: print(json.dumps(execute(a.db,a.holder,a.epoch,a.plan,a.signature,a.approval_verifier,a.adapter,a.state_root),sort_keys=True)); return 0
    except HermesError as exc: print(json.dumps({"error":str(exc)},sort_keys=True)); return 2


if __name__=="__main__": raise SystemExit(main())
