#!/usr/bin/env python3
"""Execute one provider-neutral task through an explicitly selected executor."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import pwd
import re
import shutil
import signal
import stat
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import yaml

from hermes_common import HermesError, SHA, atomic_json, ensure_private_dir, load_json, require_id
import workspace_manager

BASE_ENV = ("PATH", "LANG", "LC_ALL", "SSL_CERT_FILE", "SSL_CERT_DIR")
RESERVED_ENV = set(BASE_ENV) | {"HOME","CODEX_HOME","GH_CONFIG_DIR"}
TASK_REQUIRED = {"schema_version","task_id","profile","agent","repository","base_sha","branch","executor","instruction","timeout_seconds","credential_aliases","validation","external_actions","recovery_state"}
TASK_OPTIONAL = {"sop_id","binding","pull_request"}


@contextmanager
def active_workspace_lock(state: Path, task_id: str):
    path=state/"locks"/f"task-{require_id(task_id,'task id')}.lock"
    ensure_private_dir(path.parent)
    with path.open("a+",encoding="utf-8") as handle:
        try: fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc: raise HermesError("task is already executing") from exc
        yield


def terminate(process: subprocess.Popen, grace: int = 10) -> int:
    if process.poll() is not None: return process.returncode
    os.killpg(process.pid,signal.SIGTERM)
    try: return process.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid,signal.SIGKILL)
        return process.wait()


def validate_contract(task: dict) -> None:
    if not isinstance(task,dict) or not TASK_REQUIRED <= set(task) or set(task)-TASK_REQUIRED-TASK_OPTIONAL or task.get("schema_version")!=1:
        raise HermesError("invalid task manifest contract")
    for key in ("task_id","profile","agent"):
        require_id(task.get(key,""),key.replace("_"," "))
    if not isinstance(task.get("repository"),str) or task["repository"].count("/")!=1 or not SHA.fullmatch(task.get("base_sha", "")):
        raise HermesError("invalid task repository identity")
    branch=task.get("branch")
    if branch is not None and (not isinstance(branch,str) or not (branch.startswith("hermes/") or branch.startswith("codex/"))):
        raise HermesError("invalid task branch")
    if task.get("executor")!="codex" or not isinstance(task.get("instruction"),str) or not task["instruction"].strip():
        raise HermesError("invalid task executor contract")
    timeout=task.get("timeout_seconds")
    if isinstance(timeout,bool) or not isinstance(timeout,int) or not 1<=timeout<=86400:
        raise HermesError("invalid timeout")
    aliases=task.get("credential_aliases"); validation=task.get("validation"); actions=task.get("external_actions")
    if not isinstance(aliases,list): raise HermesError("invalid credential aliases")
    for alias in aliases: require_id(alias,"credential alias")
    if len(set(aliases))!=len(aliases): raise HermesError("invalid credential aliases")
    if not isinstance(validation,list) or any(not isinstance(item,str) or not item for item in validation): raise HermesError("invalid validation contract")
    if not isinstance(actions,list): raise HermesError("invalid external action contract")
    for action in actions:
        if not isinstance(action,dict) or set(action)!={"action_type","target_alias","idempotency_key","policy_decision"}: raise HermesError("invalid external action contract")
        for key in ("action_type","target_alias","idempotency_key"): require_id(action.get(key,""),key.replace("_"," "))
        if action.get("policy_decision") not in {"allowed","approval-required","prohibited"}: raise HermesError("invalid external action policy")
    effect_aliases={action["target_alias"] for action in actions}
    if effect_aliases & set(aliases): raise HermesError("effecting credentials are available only to the fenced provider broker")
    if task.get("recovery_state") not in {"clean","preserved","blocked"}: raise HermesError("invalid recovery state")


def isolated_env(runtime_root: Path, profile: str, task_id: str, executor: dict,
                 credential_broker: Path | None, aliases: list[str]) -> dict[str, str]:
    home = runtime_root / "homes" / profile / task_id
    codex_home = runtime_root / "codex" / profile / task_id
    gh_home = runtime_root / "gh" / profile / task_id
    for path in (home, codex_home, gh_home): ensure_private_dir(path)
    allowed = set(BASE_ENV) & set(executor.get("environment_allowlist", BASE_ENV))
    env = {key: os.environ[key] for key in allowed if key in os.environ}
    env.update({"HOME": str(home), "CODEX_HOME": str(codex_home), "GH_CONFIG_DIR": str(gh_home)})
    mapping=executor.get("credential_environment",{})
    if not isinstance(mapping,dict) or any(not isinstance(key,str) or not isinstance(value,str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*",value) or value in RESERVED_ENV for key,value in mapping.items()):
        raise HermesError("invalid executor credential environment mapping")
    if not isinstance(aliases, list) or any(not isinstance(alias, str) for alias in aliases):
        raise HermesError("credential aliases must be a list of identifiers")
    aliases = [require_id(alias, "credential alias") for alias in aliases]
    file_mapping = credential_file_mapping(executor)
    if set(mapping) & set(file_mapping):
        raise HermesError("credential alias cannot map to both environment and file")
    environment_aliases = [alias for alias in aliases if alias not in file_mapping]
    if environment_aliases:
        if credential_broker is None: raise HermesError("credential aliases require broker")
        result = subprocess.run([str(credential_broker), "resolve-task", profile, task_id, *environment_aliases], text=True,
                                capture_output=True, env={"PATH": env.get("PATH", "")}, check=False)
        if result.returncode: raise HermesError("credential broker denied requested aliases")
        try: resolved = json.loads(result.stdout)
        except json.JSONDecodeError as exc: raise HermesError("credential broker returned invalid response") from exc
        if not isinstance(resolved, dict) or set(resolved) != set(environment_aliases):
            raise HermesError("credential broker returned unexpected aliases")
        if any(not isinstance(value, str) for value in resolved.values()):
            raise HermesError("credential broker returned a non-string value")
        # Values are injected only into this child process and never written to receipts.
        for key,value in resolved.items():
            env[mapping.get(key,f"HERMES_CREDENTIAL_{key.upper().replace('-', '_')}")]=value
    return env


def credential_file_mapping(executor: dict) -> dict[str, str]:
    mapping = executor.get("credential_files", {})
    if not isinstance(mapping, dict):
        raise HermesError("invalid executor credential file mapping")
    for alias, filename in mapping.items():
        require_id(alias, "credential alias")
        if (not isinstance(filename, str) or not filename or filename in {".", ".."}
                or Path(filename).name != filename or "/" in filename or "\\" in filename):
            raise HermesError("invalid executor credential file mapping")
    return mapping


def _validate_private_credential_file(path: Path) -> None:
    try: facts = path.lstat()
    except FileNotFoundError as exc: raise HermesError("credential broker did not materialize credential file") from exc
    if not stat.S_ISREG(facts.st_mode) or path.is_symlink() or facts.st_uid != os.geteuid() or stat.S_IMODE(facts.st_mode) != 0o600:
        raise HermesError("credential broker materialized unsafe credential file")


def materialize_credential_files(runtime_root: Path, profile: str, task_id: str, executor: dict,
                                 credential_broker: Path | None, aliases: list[str]) -> dict[str, Path]:
    mapping = credential_file_mapping(executor)
    requested = {alias: mapping[alias] for alias in aliases if alias in mapping}
    if not requested: return {}
    if credential_broker is None: raise HermesError("credential file aliases require broker")
    codex_home = runtime_root / "codex" / profile / task_id
    ensure_private_dir(codex_home)
    materialized: dict[str, Path] = {}
    try:
        for alias, filename in requested.items():
            destination = codex_home / filename
            if destination.exists() or destination.is_symlink():
                raise HermesError("credential destination already exists")
            result = subprocess.run(
                [str(credential_broker), "materialize-task", profile, task_id, alias, str(destination)],
                text=True, capture_output=True, env={"PATH": os.environ.get("PATH", "")}, check=False,
            )
            if result.returncode:
                raise HermesError("credential broker denied credential file materialization")
            _validate_private_credential_file(destination)
            materialized[alias] = destination
        return materialized
    except BaseException:
        for path in [*(materialized.values()), *(codex_home / name for name in requested.values())]:
            try:
                if path.is_file() or path.is_symlink(): path.unlink()
            except OSError: pass
        raise


def persist_credential_files(profile: str, task_id: str, credential_broker: Path | None,
                             materialized: dict[str, Path]) -> None:
    if not materialized: return
    if credential_broker is None: raise HermesError("credential file aliases require broker")
    failures = []
    for alias, path in materialized.items():
        try:
            _validate_private_credential_file(path)
            result = subprocess.run(
                [str(credential_broker), "persist-task", profile, task_id, alias, str(path)],
                text=True, capture_output=True, env={"PATH": os.environ.get("PATH", "")}, check=False,
            )
            if result.returncode: raise HermesError("credential broker denied credential file persistence")
            path.unlink()
        except (HermesError, OSError) as exc:
            failures.append(alias)
    if failures:
        raise HermesError("credential persistence failed; private recovery copy preserved")


def _run_task(contract_path: Path, workspace: Path, workspace_receipt: Path,
              executor_path: Path, state: Path, runtime_root: Path,
              credential_broker: Path | None = None, cancel_file: Path | None = None,
              core_verifier: Path | None = None) -> dict:
    task = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
    executor = yaml.safe_load(executor_path.read_text(encoding="utf-8")) or {}
    receipt = load_json(workspace_receipt)
    validate_contract(task)
    task_id = require_id(task.get("task_id", ""), "task id")
    profile = require_id(task.get("profile", ""), "profile")
    if executor.get("id") != task.get("executor") or executor.get("fallback") != "prohibited":
        raise HermesError("executor mismatch or fallback not prohibited")
    user_template=executor.get("required_user_template")
    if not isinstance(user_template,str) or user_template.format(profile=profile)!=pwd.getpwuid(os.geteuid()).pw_name:
        raise HermesError("task executor must run under its isolated profile task user")
    for field in ("agent", "repository", "base_sha"):
        if task.get(field) != receipt.get(field): raise HermesError(f"task/workspace {field} mismatch")
    if task_id != receipt.get("task_id") or Path(receipt["workspace"]).resolve() != workspace.resolve():
        raise HermesError("task/workspace identity mismatch")
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=workspace, text=True).strip()
    actual_branch = None if branch == "HEAD" else branch
    if actual_branch != task.get("branch"): raise HermesError("workspace branch mismatch")
    workspace_facts=workspace_manager.inspect(workspace,receipt)
    if workspace_facts["head_sha"]!=receipt.get("head_sha") or workspace_facts["dirty"]:
        raise HermesError("workspace changed after SHA-bound provisioning")
    if core_verifier is None or not core_verifier.is_file():
        raise HermesError("CORE_VERIFIER_REQUIRED")
    checked = subprocess.run(
        [str(core_verifier), str(workspace)], cwd=workspace, shell=False,
        env={"PATH": os.environ.get("PATH", "")}, text=True, capture_output=True,
    )
    if checked.returncode: raise HermesError("pinned core bundle verification failed")
    binary = executor.get("command")
    if not isinstance(binary, str) or not shutil.which(binary): raise HermesError("BLOCKED_EXECUTOR_UNAVAILABLE")
    instruction = task["instruction"]
    aliases = task.get("credential_aliases", [])
    env = isolated_env(runtime_root, profile, task_id, executor, credential_broker, aliases)
    file_mapping = credential_file_mapping(executor)
    credential_file_aliases = sorted(alias for alias in aliases if alias in file_mapping)
    timeout = task["timeout_seconds"]
    receipt_file = state / "task-receipts" / f"{task_id}.json"
    log_file = state / "task-logs" / profile / f"{task_id}.log"
    ensure_private_dir(log_file.parent)
    receipt_context = {
        "schema_version": 1, "task_id": task_id, "profile": profile,
        "repository": task["repository"], "base_sha": task["base_sha"],
        "branch": task.get("branch"), "executor": executor["id"],
        "core_verified": True, "credential_aliases": aliases,
        "credential_file_aliases": credential_file_aliases,
        "validation": task.get("validation", []),
        "external_actions": task.get("external_actions", []),
        "recovery_state": task.get("recovery_state", "blocked"),
        "log_file": str(log_file),
    }
    started = time.time(); status = "running"; error = None; code = None
    atomic_json(receipt_file, {**receipt_context, "status":status,"started_at":started})
    process = None
    credential_files: dict[str, Path] = {}
    try:
        credential_files = materialize_credential_files(runtime_root, profile, task_id, executor, credential_broker, aliases)
        with log_file.open("ab", buffering=0) as log:
            os.chmod(log_file, 0o600)
            process = subprocess.Popen(
                [binary, "exec", "--cd", str(workspace), "--", instruction],
                cwd=workspace, env=env, start_new_session=True, stdout=log, stderr=log,
            )
            while code is None:
                if cancel_file and cancel_file.exists():
                    status = "cancelled"; error = "cancel requested"
                    code = terminate(process); break
                if time.time() - started > timeout:
                    status = "timed-out"; error = "timeout exceeded"
                    code = terminate(process)
                    break
                code = process.poll()
                if code is None: time.sleep(0.1)
            if status == "running": status = "succeeded" if code == 0 else "failed"
            if status == "failed": error = f"executor exited {code}"
    except BaseException as exc:
        status = "error"; error = str(exc) if isinstance(exc, HermesError) else type(exc).__name__
        if process is not None: code = terminate(process)
    credential_persistence = "not-required"
    try:
        persist_credential_files(profile, task_id, credential_broker, credential_files)
        if credential_files: credential_persistence = "persisted"
    except HermesError as exc:
        status = "error"; error = str(exc); credential_persistence = "failed"
        receipt_context["recovery_state"] = "blocked"
    final = {**receipt_context, "status":status,"exit_code":code,
             "started_at":started,"finished_at":time.time(),"error":error,
             "credential_persistence": credential_persistence}
    atomic_json(receipt_file, final)
    return final


def run_task(contract_path: Path, workspace: Path, workspace_receipt: Path,
             executor_path: Path, state: Path, runtime_root: Path,
             credential_broker: Path | None = None, cancel_file: Path | None = None,
             core_verifier: Path | None = None) -> dict:
    try:
        receipt=load_json(workspace_receipt)
        if Path(receipt.get("state_root","")).absolute()!=state.absolute(): raise HermesError("workspace receipt state root mismatch")
        with active_workspace_lock(state,receipt.get("task_id","")):
            return _run_task(
                contract_path, workspace, workspace_receipt, executor_path, state,
                runtime_root, credential_broker, cancel_file, core_verifier,
            )
    except HermesError as exc:
        try:
            task = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
            task_id = require_id(task.get("task_id", ""), "task id")
            profile = require_id(task.get("profile", ""), "profile")
            atomic_json(
                state / "task-receipts" / f"{task_id}.json",
                {"schema_version": 1, "task_id": task_id, "profile": profile,
                 "status": "blocked", "error": str(exc),
                 "finished_at": time.time(), "recovery_state": "blocked"},
            )
        except Exception:
            pass
        raise


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--contract",type=Path,required=True); p.add_argument("--workspace",type=Path,required=True); p.add_argument("--workspace-receipt",type=Path,required=True); p.add_argument("--executor",type=Path,required=True); p.add_argument("--state",type=Path,required=True); p.add_argument("--runtime-root",type=Path,required=True); p.add_argument("--credential-broker",type=Path); p.add_argument("--cancel-file",type=Path); p.add_argument("--core-verifier",type=Path,required=True)
    a=p.parse_args()
    try: result=run_task(a.contract,a.workspace,a.workspace_receipt,a.executor,a.state,a.runtime_root,a.credential_broker,a.cancel_file,a.core_verifier); print(json.dumps(result,sort_keys=True)); return 0 if result["status"]=="succeeded" else 1
    except HermesError as exc: print(json.dumps({"status":"blocked","error":str(exc)},sort_keys=True)); return 2
if __name__=="__main__": raise SystemExit(main())
