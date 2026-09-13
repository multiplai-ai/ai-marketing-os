#!/usr/bin/env python3
"""Provision fresh, identity-verified task workspaces without destroying work."""
from __future__ import annotations

import argparse
import fcntl
import json
import shutil
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import yaml

from hermes_common import (HermesError, SHA, atomic_json, canonical_child,
                           load_json, require_id, run)


@contextmanager
def locked(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def _repo(registry: Path, repo_id: str) -> dict:
    require_id(repo_id, "repository id")
    data = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
    matches = [r for r in data.get("repositories", []) if r.get("id") == repo_id]
    if len(matches) != 1:
        raise HermesError(f"repository is not uniquely allowlisted: {repo_id}")
    spec = matches[0]
    if not spec.get("remote_url") or not spec.get("github"):
        raise HermesError("repository requires explicit remote_url and github identity")
    return spec


def _normalize_remote(value: str) -> str:
    value = value.removesuffix(".git").rstrip("/")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    return value


def _assert_identity(workspace: Path, spec: dict) -> None:
    actual = _normalize_remote(run(["git", "remote", "get-url", "origin"], workspace))
    remote = spec.get("remote_url")
    github = spec.get("github") or spec.get("repository")
    if not isinstance(remote, str) or not remote or not isinstance(github, str) or github.count("/") != 1:
        raise HermesError("repository receipt identity is incomplete")
    expected = _normalize_remote(remote)
    if actual != expected:
        raise HermesError("repository remote identity mismatch")
    if "github.com" in expected and not expected.endswith("/" + github):
        raise HermesError("repository GitHub identity mismatch")


def _receipt_path(state: Path, task_id: str) -> Path:
    return canonical_child(state, "receipts", f"{require_id(task_id, 'task id')}.json")


def create(registry: Path, root: Path, state: Path, agent: str, repo_id: str,
           task_id: str, writable: bool, branch: str | None = None) -> dict:
    require_id(agent, "agent")
    require_id(task_id, "task id")
    spec = _repo(registry, repo_id)
    if agent not in set(spec.get("allowed_agents") or []):
        raise HermesError("agent is not allowlisted for repository")
    default = spec.get("default_branch")
    allowed = set(spec.get("allowed_branches") or [default])
    prefixes = tuple(spec.get("allowed_branch_prefixes") or [])
    if default not in allowed:
        raise HermesError("default branch is not allowlisted")
    if branch and not writable:
        raise HermesError("detached workspace cannot resume a PR branch")
    if branch and not (branch.startswith("codex/") or branch.startswith(f"hermes/{agent}/")):
        raise HermesError("resumed branch has an invalid owner prefix")
    if branch and branch not in allowed and not any(branch.startswith(prefix) for prefix in prefixes):
        raise HermesError("resumed branch is not allowlisted")
    destination = canonical_child(root, agent, task_id)
    receipt_file = _receipt_path(state, task_id)
    with locked(canonical_child(state, "locks", f"{repo_id}.lock")):
        if destination.exists() or receipt_file.exists():
            raise HermesError("task workspace or receipt already exists")
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        run(["git", "clone", "--no-checkout", "--origin", "origin", spec["remote_url"], str(destination)])
        try:
            _assert_identity(destination, spec)
            run(["git", "fetch", "--prune", "origin", default], destination)
            base = run(["git", "rev-parse", f"origin/{default}^{{commit}}"], destination)
            if not SHA.fullmatch(base):
                raise HermesError("fetched base is not a commit SHA")
            if branch:
                run(["git", "fetch", "origin", f"refs/heads/{branch}:refs/remotes/origin/{branch}"], destination)
                tip = run(["git", "rev-parse", f"origin/{branch}^{{commit}}"], destination)
                run(["git", "checkout", "-b", branch, tip], destination)
                mode = "resume"
            elif writable:
                branch = f"hermes/{agent}/{task_id}"
                if branch not in allowed and not any(branch.startswith(prefix) for prefix in prefixes):
                    raise HermesError("task branch prefix is not allowlisted")
                run(["git", "checkout", "-b", branch, base], destination)
                mode = "writable"
            else:
                run(["git", "checkout", "--detach", base], destination)
                mode = "detached"
            head = run(["git", "rev-parse", "HEAD"], destination)
            receipt = {
                "schema_version": 1, "task_id": task_id, "agent": agent,
                "repo_id": repo_id, "repository": spec["github"],
                "remote_url": spec["remote_url"], "default_branch": default,
                "base_sha": base, "head_sha": head, "branch": branch,
                "mode": mode, "workspace": str(destination),
                "task_root": str(root.absolute()), "state_root": str(state.absolute()),
                "created_at": int(time.time()),
            }
            atomic_json(receipt_file, receipt)
            atomic_json(destination / ".hermes-workspace.json", {"task_id": task_id}, mode=0o444)
            return receipt
        except Exception:
            if destination.exists():
                shutil.rmtree(destination)
            raise


def inspect(workspace: Path, receipt: dict, refresh_remote: bool = False) -> dict:
    expected = canonical_child(
        Path(receipt["task_root"]), receipt["agent"], receipt["task_id"],
        must_exist=True,
    )
    if workspace.absolute() != expected or workspace.resolve() != Path(receipt["workspace"]).resolve():
        raise HermesError("workspace receipt path mismatch")
    _assert_identity(workspace, receipt)
    status = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], workspace)
    head = run(["git", "rev-parse", "HEAD"], workspace)
    base = receipt["base_sha"]
    ahead = int(run(["git", "rev-list", "--count", f"{base}..HEAD"], workspace))
    marker_only = status.strip() == "?? .hermes-workspace.json"
    dirty = bool(status) and not marker_only
    unpushed = 0
    remote_reachable = True
    branch = receipt.get("branch")
    if branch:
        if refresh_remote:
            refreshed = subprocess.run(
                ["git", "fetch", "--prune", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}"],
                cwd=workspace, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, check=False,
            )
            if refreshed.returncode:
                return {"head_sha": head, "dirty": dirty, "ahead_of_base": ahead,
                        "unpushed_commits": max(ahead, 1), "remote_reachable": False,
                        "preserve": True, "remote_refresh_failed": True,
                        "status_lines": status.splitlines() if status else []}
        remote_ref = f"refs/remotes/origin/{branch}"
        exists = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", remote_ref], cwd=workspace,
            check=False,
        ).returncode == 0
        if exists:
            unpushed = int(run(["git", "rev-list", "--count", f"{remote_ref}..HEAD"], workspace))
            remote_reachable = subprocess.run(
                ["git", "merge-base", "--is-ancestor", "HEAD", remote_ref],
                cwd=workspace, check=False,
            ).returncode == 0
        else:
            unpushed = ahead
            remote_reachable = ahead == 0
    return {"head_sha": head, "dirty": dirty, "ahead_of_base": ahead,
            "unpushed_commits": unpushed, "remote_reachable": remote_reachable,
            "preserve": dirty or unpushed > 0 or not remote_reachable,
            "status_lines": status.splitlines() if status else []}


def inventory(root: Path, state: Path) -> list[dict]:
    result = []
    receipts = canonical_child(state, "receipts")
    if not receipts.exists():
        return result
    for path in sorted(receipts.glob("*.json")):
        receipt = load_json(path)
        workspace = Path(receipt["workspace"])
        row = {"task_id": receipt["task_id"], "workspace": str(workspace)}
        if not workspace.exists():
            row.update({"state": "missing", "preserve": True})
        else:
            row.update({"state": "present", **inspect(workspace, receipt)})
        result.append(row)
    return result


def cleanup(workspace: Path, state: Path, task_id: str) -> dict:
    receipt_file = _receipt_path(state, task_id)
    receipt = load_json(receipt_file)
    if Path(receipt.get("state_root", "")).absolute() != state.absolute():
        raise HermesError("workspace receipt state root mismatch")
    task_lock=canonical_child(state,"locks",f"task-{require_id(task_id,'task id')}.lock")
    task_lock.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with task_lock.open("a+",encoding="utf-8") as handle:
        try: fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            return {"removed":False,"reason":"workspace is actively executing","preserve":True,"workspace":str(workspace)}
        with locked(canonical_child(state,"locks",f"{receipt['repo_id']}.lock")):
            facts = inspect(workspace, receipt, refresh_remote=True)
            if facts["preserve"]:
                return {"removed": False, "reason": "workspace has dirty, unpushed, or unverified remote work", **facts}
            shutil.rmtree(workspace)
            receipt_file.unlink()
            return {"removed": True, "workspace": str(workspace)}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create_p = sub.add_parser("create")
    for name in ("registry", "root", "state"):
        create_p.add_argument(f"--{name}", type=Path, required=True)
    create_p.add_argument("--agent", required=True); create_p.add_argument("--repo", required=True)
    create_p.add_argument("--task", required=True); create_p.add_argument("--writable", action="store_true")
    create_p.add_argument("--resume-branch")
    inv = sub.add_parser("inventory"); inv.add_argument("--root", type=Path, required=True); inv.add_argument("--state", type=Path, required=True)
    clean = sub.add_parser("cleanup"); clean.add_argument("workspace", type=Path); clean.add_argument("--state", type=Path, required=True); clean.add_argument("--task", required=True)
    args = parser.parse_args()
    try:
        if args.command == "create":
            value = create(args.registry, args.root, args.state, args.agent, args.repo, args.task, args.writable or bool(args.resume_branch), args.resume_branch)
        elif args.command == "inventory": value = inventory(args.root, args.state)
        else: value = cleanup(args.workspace, args.state, args.task)
        print(json.dumps(value, sort_keys=True)); return 0
    except HermesError as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True)); return 2


if __name__ == "__main__":
    raise SystemExit(main())
