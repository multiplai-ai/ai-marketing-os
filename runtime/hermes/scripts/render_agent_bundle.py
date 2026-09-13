#!/usr/bin/env python3
"""Render a minimal, immutable, signed per-profile runtime bundle."""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, tempfile, time
from pathlib import Path
import yaml
from hermes_common import HermesError, SHA, atomic_json, canonical_child, require_id, sha256_file

VERSION=re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")


def render(spec_path: Path, output_root: Path, signer: Path | None) -> Path:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    if not isinstance(spec,dict) or set(spec)!={"profile","version","revision","core_commit","control_commit","files"}: raise HermesError("invalid bundle specification")
    profile = require_id(spec.get("profile", ""), "profile")
    version = spec.get("version"); revision = spec.get("revision"); commit = spec.get("core_commit"); control_commit = spec.get("control_commit")
    if not isinstance(version, str) or not VERSION.fullmatch(version) or isinstance(revision,bool) or not isinstance(revision, int) or revision < 1 or not SHA.fullmatch(commit or "") or not SHA.fullmatch(control_commit or ""):
        raise HermesError("invalid bundle version, revision, core commit, or control commit")
    if not isinstance(spec["files"],list) or not spec["files"]: raise HermesError("bundle must contain files")
    final = canonical_child(output_root, profile, f"{version}-r{revision}")
    if final.exists(): raise HermesError("immutable bundle already exists")
    final.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".bundle-", dir=final.parent))
    try:
        files = {}
        for item in spec.get("files", []):
            if not isinstance(item,dict) or not {"source","destination"}<=set(item) or set(item)-{"source","destination","executable"}: raise HermesError("invalid bundle file contract")
            if not isinstance(item["source"],str) or not isinstance(item["destination"],str): raise HermesError("invalid bundle file contract")
            source = Path(item["source"])
            destination = canonical_child(staging, item["destination"])
            if source.is_symlink() or not source.is_file(): raise HermesError("bundle source must be a regular non-symlink file")
            if item["destination"] in files: raise HermesError("duplicate bundle destination")
            destination.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, destination); os.chmod(destination, 0o555 if item.get("executable") else 0o444)
            files[item["destination"]] = sha256_file(destination)
        manifest = {"schema_version":1,"profile":profile,"version":version,"revision":revision,"core_commit":commit,"control_commit":control_commit,"created_at":int(time.time()),"files":files}
        atomic_json(staging/"manifest.json",manifest,mode=0o444)
        if signer:
            result=subprocess.run([str(signer),str(staging/"manifest.json"),str(staging/"manifest.sig")],capture_output=True,text=True)
            if result.returncode or not (staging/"manifest.sig").is_file(): raise HermesError("bundle signing failed")
            os.chmod(staging/"manifest.sig",0o444)
        else: raise HermesError("unsigned bundles are prohibited")
        for path in sorted(staging.rglob("*"), reverse=True):
            if path.is_dir(): os.chmod(path, 0o555)
        os.replace(staging,final)
        os.chmod(final, 0o555)
        return final
    except Exception:
        shutil.rmtree(staging,ignore_errors=True); raise


def main():
 p=argparse.ArgumentParser(); p.add_argument("--spec",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--signer",type=Path,required=True); a=p.parse_args()
 try: print(render(a.spec,a.output,a.signer)); return 0
 except HermesError as e: print(json.dumps({"error":str(e)})); return 2
if __name__=="__main__": raise SystemExit(main())
