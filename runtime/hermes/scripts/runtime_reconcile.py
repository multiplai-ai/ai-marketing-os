#!/usr/bin/env python3
"""Verify and atomically activate a runtime bundle with rollback state."""
from __future__ import annotations
import sys

# Reconciliation runs as root against an immutable exact-file-set bundle.
# Suppress import caches before loading any sibling module so verification
# cannot mutate and then reject its own candidate.
sys.dont_write_bytecode = True

import argparse, fcntl, json, os, re, shutil, subprocess, tempfile, time
from contextlib import contextmanager
from pathlib import Path
from hermes_common import HermesError, SHA, atomic_json, canonical_child, fsync_dir, load_json, require_id, sha256_file

VERSION=re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
MANIFEST_KEYS={"schema_version","profile","version","revision","core_commit","control_commit","created_at","files"}


@contextmanager
def profile_lock(state_root: Path, profile: str):
    path=canonical_child(state_root,"locks",f"reconcile-{require_id(profile,'profile')}.lock")
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with path.open("a+",encoding="utf-8") as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        yield


def _remove_tree(path: Path) -> None:
    if not path.exists(): return
    for candidate in sorted(path.rglob("*"), reverse=True):
        if candidate.is_dir(): os.chmod(candidate, 0o700)
        elif candidate.is_file(): os.chmod(candidate, 0o600)
    os.chmod(path, 0o700)
    shutil.rmtree(path)


def verify(bundle: Path, verifier: Path) -> dict:
    if bundle.is_symlink() or not bundle.is_dir(): raise HermesError("unsafe bundle path")
    if any(path.is_symlink() for path in bundle.rglob("*")):
        raise HermesError("bundle must not contain symlinks")
    manifest=load_json(bundle/"manifest.json")
    result=subprocess.run([str(verifier),str(bundle/"manifest.json"),str(bundle/"manifest.sig")],capture_output=True,text=True)
    if result.returncode: raise HermesError("bundle trust verification failed")
    if not isinstance(manifest,dict) or set(manifest)!=MANIFEST_KEYS or manifest.get("schema_version")!=1: raise HermesError("invalid bundle manifest")
    try: require_id(manifest.get("profile",""),"bundle profile")
    except HermesError as exc: raise HermesError("invalid bundle manifest") from exc
    if not isinstance(manifest.get("version"),str) or not VERSION.fullmatch(manifest["version"]): raise HermesError("invalid bundle manifest")
    if isinstance(manifest.get("revision"),bool) or not isinstance(manifest.get("revision"),int) or manifest["revision"]<1: raise HermesError("invalid bundle manifest")
    if not SHA.fullmatch(manifest.get("core_commit", "")) or not SHA.fullmatch(manifest.get("control_commit", "")): raise HermesError("invalid bundle manifest")
    if isinstance(manifest.get("created_at"),bool) or not isinstance(manifest.get("created_at"),int) or manifest["created_at"]<0: raise HermesError("invalid bundle manifest")
    if not isinstance(manifest.get("files"),dict) or not manifest["files"]: raise HermesError("invalid bundle manifest")
    if any(not isinstance(rel,str) or not isinstance(digest,str) or not re.fullmatch(r"[0-9a-f]{64}",digest) for rel,digest in manifest["files"].items()): raise HermesError("invalid bundle manifest")
    expected=set(manifest.get("files",{})); actual={str(p.relative_to(bundle)) for p in bundle.rglob("*") if p.is_file()}-{"manifest.json","manifest.sig"}
    if expected!=actual: raise HermesError("bundle file set mismatch")
    for rel,digest in manifest["files"].items():
        path=canonical_child(bundle,rel,must_exist=True)
        if path.is_symlink() or sha256_file(path)!=digest: raise HermesError(f"bundle checksum mismatch: {rel}")
    return manifest


def recover_pending(state_file: Path, profile_root: Path, releases: Path, profile: str, verifier: Path) -> dict:
    """Fail closed after a crash between activation intent and committed state."""
    state=load_json(state_file) if state_file.exists() else {}
    if state.get("phase")=="rolling-back":
        target=Path(state.get("target") or "")
        try: target.resolve().relative_to(releases.resolve())
        except ValueError as exc: raise HermesError("pending rollback path escapes managed releases") from exc
        restored=verify(target,verifier)
        if restored.get("profile")!=profile: raise HermesError("pending rollback profile mismatch")
        current=profile_root/"current"; temp=current.with_name(".current.recover-rollback"); temp.unlink(missing_ok=True); temp.symlink_to(target); os.replace(temp,current); fsync_dir(profile_root)
        result=state.get("result_state")
        if not isinstance(result,dict): raise HermesError("pending rollback result is invalid")
        atomic_json(state_file,result); return result
    if state.get("phase")!="activating": return state
    candidate=Path(state["candidate"]) if state.get("candidate") else None
    previous=Path(state["previous"]) if state.get("previous") else None
    for path in (candidate,previous):
        if path is not None:
            try: path.resolve().relative_to(releases.resolve())
            except ValueError as exc: raise HermesError("pending reconciliation path escapes managed releases") from exc
    current=profile_root/"current"; temp=current.with_name(".current.recover"); temp.unlink(missing_ok=True)
    if previous is not None and previous.is_dir():
        restored=verify(previous,verifier)
        if restored.get("profile")!=profile: raise HermesError("pending rollback profile mismatch")
        temp.symlink_to(previous); os.replace(temp,current); fsync_dir(profile_root)
    else: current.unlink(missing_ok=True)
    if candidate is not None and candidate.is_dir() and candidate!=previous: _remove_tree(candidate)
    prior=state.get("prior_state") or {"phase":"inactive","profile":profile,"revision":0,"writer_enablement":"disabled"}
    atomic_json(state_file,prior)
    return prior


def _reconcile(bundle: Path, deploy_root: Path, profile: str, state_root: Path, verifier: Path, health: list[str]) -> dict:
    require_id(profile, "profile")
    if not health or any(not isinstance(item,str) or not item for item in health): raise HermesError("health command required")
    manifest=verify(bundle,verifier)
    if manifest.get("profile")!=profile: raise HermesError("bundle profile mismatch")
    profile_root=canonical_child(deploy_root,profile); releases=canonical_child(profile_root,"releases"); releases.mkdir(parents=True,exist_ok=True)
    state_file=canonical_child(state_root,"reconcile",f"{profile}.json")
    previous_state=recover_pending(state_file,profile_root,releases,profile,verifier)
    if manifest["revision"]<=previous_state.get("revision",0): raise HermesError("bundle replay or downgrade prohibited")
    staged=canonical_child(releases,f"{manifest['version']}-r{manifest['revision']}")
    if staged.exists(): raise HermesError("release generation already staged")
    shutil.copytree(bundle,staged,symlinks=False)
    # Reverify the staged copy to close the verify/copy race.
    verify(staged, verifier)
    current=profile_root/"current"; old=current.resolve() if current.is_symlink() and current.exists() else None
    if old is not None:
        try: old.relative_to(releases.resolve())
        except ValueError as exc: raise HermesError("current release escapes managed releases") from exc
    pending={"phase":"activating","profile":profile,"version":manifest["version"],"revision":manifest["revision"],"candidate":str(staged),"previous":str(old) if old else None,"prior_state":previous_state,"intent_recorded_at":int(time.time())}
    atomic_json(state_file,pending)
    temp=current.with_name(".current.new"); temp.unlink(missing_ok=True); temp.symlink_to(staged); os.replace(temp,current); fsync_dir(profile_root)
    try:
        checked=subprocess.run(health,cwd=current,capture_output=True,text=True,timeout=60)
        if checked.returncode: raise HermesError("new runtime failed pre-writer health check")
    except (HermesError,OSError,subprocess.TimeoutExpired) as exc:
        # Health runs before writer enablement; every failure path rolls back.
        temp.unlink(missing_ok=True)
        if old: temp.symlink_to(old); os.replace(temp,current)
        else: current.unlink(missing_ok=True)
        fsync_dir(profile_root)
        _remove_tree(staged)
        atomic_json(state_file,previous_state or {"phase":"inactive","profile":profile,"revision":0,"writer_enablement":"disabled"})
        raise HermesError("new runtime failed pre-writer health check and was rolled back") from exc
    state={"phase":"active","profile":profile,"version":manifest["version"],"revision":manifest["revision"],"bundle":str(staged),"previous":str(old) if old else None,"activated_at":int(time.time()),"writer_enablement":"requires-supervisor"}
    atomic_json(state_file,state); return state


def reconcile(bundle: Path, deploy_root: Path, profile: str, state_root: Path, verifier: Path, health: list[str]) -> dict:
    with profile_lock(state_root,profile):
        return _reconcile(bundle,deploy_root,profile,state_root,verifier,health)


def mark_writer_enabled(state_root: Path, profile: str, version: str, revision: int) -> dict:
    """Record the separately supervised point after which rollback is effect-aware."""
    with profile_lock(state_root,profile):
        state_file=canonical_child(state_root,"reconcile",f"{profile}.json",must_exist=True); state=load_json(state_file)
        if state.get("version")!=version or state.get("revision")!=revision: raise HermesError("generation changed before writer enablement")
        state["writer_enablement"]="enabled"; state["writer_enabled_at"]=int(time.time()); atomic_json(state_file,state); return state


def supervised_rollback(deploy_root: Path, state_root: Path, profile: str, approval: str, verifier: Path) -> dict:
    """Rollback after possible effects only with an exact, generation-bound approval."""
    with profile_lock(state_root,profile):
        state_file=canonical_child(state_root,"reconcile",f"{profile}.json",must_exist=True); state=load_json(state_file)
        expected=f"{profile}:{state['version']}:r{state['revision']}"
        if state.get("writer_enablement")=="enabled" and approval!=expected: raise HermesError("post-effect rollback requires generation-bound supervisor approval")
        previous=Path(state.get("previous") or "")
        if not previous.is_dir(): raise HermesError("no verified previous generation available")
        profile_root=canonical_child(deploy_root,profile); releases=canonical_child(profile_root,"releases",must_exist=True)
        try: previous.resolve().relative_to(releases.resolve())
        except ValueError as exc: raise HermesError("previous release escapes managed releases") from exc
        previous_manifest=verify(previous,verifier)
        if previous_manifest.get("profile")!=profile: raise HermesError("previous release profile mismatch")
        result={**state,"phase":"rolled-back","rolled_back_at":int(time.time()),"rolled_back_from":state["bundle"],"bundle":str(previous),"writer_enablement":"disabled-pending-reconciliation"}
        pending={"phase":"rolling-back","profile":profile,"target":str(previous),"from":state["bundle"],"result_state":result,"intent_recorded_at":int(time.time())}
        atomic_json(state_file,pending)
        current=profile_root/"current"; temp=current.with_name(".current.rollback"); temp.unlink(missing_ok=True); temp.symlink_to(previous); os.replace(temp,current); fsync_dir(profile_root)
        atomic_json(state_file,result); return result


def main():
 p=argparse.ArgumentParser(); p.add_argument("--bundle",type=Path,required=True); p.add_argument("--deploy-root",type=Path,required=True); p.add_argument("--profile",required=True); p.add_argument("--state-root",type=Path,required=True); p.add_argument("--verifier",type=Path,required=True); p.add_argument("--health",nargs="+",required=True); a=p.parse_args()
 try: print(json.dumps(reconcile(a.bundle,a.deploy_root,a.profile,a.state_root,a.verifier,a.health),sort_keys=True)); return 0
 except (HermesError,subprocess.TimeoutExpired) as e: print(json.dumps({"error":str(e)})); return 2
if __name__=="__main__": raise SystemExit(main())
