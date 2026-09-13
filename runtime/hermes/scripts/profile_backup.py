#!/usr/bin/env python3
"""Encrypted profile backup and staged restore primitives."""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, tarfile, tempfile, time
from pathlib import Path
from hermes_common import HermesError, atomic_json, canonical_child, ensure_private_dir, fsync_dir, require_id, sha256_file


def backup(profile: str, source: Path, output: Path, encryptor: Path, snapshotter: Path) -> dict:
    require_id(profile,"profile")
    if source.is_symlink() or not source.is_dir(): raise HermesError("unsafe profile source")
    if output.is_symlink(): raise HermesError("backup output must not be a symlink")
    ensure_private_dir(output.parent)
    snapshot=Path(tempfile.mkdtemp(prefix=".snapshot-",dir=output.parent))
    fd,plain_name=tempfile.mkstemp(prefix=".profile-",suffix=".tar",dir=output.parent); os.close(fd); plain=Path(plain_name)
    fd,encrypted_name=tempfile.mkstemp(prefix=".encrypted-",dir=output.parent); os.close(fd); encrypted=Path(encrypted_name)
    try:
        snap=subprocess.run([str(snapshotter),str(source),str(snapshot)],capture_output=True,text=True)
        if snap.returncode: raise HermesError("coherent profile snapshot failed")
        with tarfile.open(plain,"w") as archive:
            for path in sorted(snapshot.rglob("*")):
                if path.is_symlink(): raise HermesError("profile backup rejects symlinks")
                if not path.is_dir() and not path.is_file(): raise HermesError("profile backup rejects special files")
                archive.add(path,arcname=path.relative_to(snapshot),recursive=False)
        result=subprocess.run([str(encryptor),str(plain),str(encrypted)],capture_output=True,text=True)
        if result.returncode or not encrypted.is_file(): raise HermesError("profile encryption failed")
        os.chmod(encrypted,0o600); os.replace(encrypted,output); fsync_dir(output.parent)
        manifest={"schema_version":1,"profile":profile,"created_at":int(time.time()),"archive":output.name,"sha256":sha256_file(output)}
        atomic_json(output.with_suffix(output.suffix+".json"),manifest); return manifest
    finally: plain.unlink(missing_ok=True); encrypted.unlink(missing_ok=True); shutil.rmtree(snapshot,ignore_errors=True)


def restore(archive: Path, manifest_path: Path, destination: Path, decryptor: Path) -> dict:
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    required={"schema_version","profile","created_at","archive","sha256"}
    if not isinstance(manifest,dict) or set(manifest)!=required or manifest.get("schema_version")!=1: raise HermesError("invalid backup manifest")
    require_id(manifest.get("profile", ""),"profile")
    if manifest.get("archive")!=archive.name or archive.is_symlink() or not archive.is_file(): raise HermesError("backup archive identity mismatch")
    if isinstance(manifest.get("created_at"),bool) or not isinstance(manifest.get("created_at"),int) or manifest["created_at"]<0: raise HermesError("invalid backup manifest")
    digest=manifest.get("sha256")
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest): raise HermesError("invalid backup manifest")
    if sha256_file(archive)!=manifest.get("sha256"): raise HermesError("backup checksum mismatch")
    if destination.is_symlink() or destination.exists(): raise HermesError("restore destination must be a new path")
    destination.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,plain_name=tempfile.mkstemp(prefix=".restore-",suffix=".tar",dir=destination.parent); os.close(fd); plain=Path(plain_name)
    staging=Path(tempfile.mkdtemp(prefix=".restore-stage-",dir=destination.parent))
    try:
        result=subprocess.run([str(decryptor),str(archive),str(plain)],capture_output=True,text=True)
        if result.returncode: raise HermesError("profile decryption failed")
        with tarfile.open(plain,"r") as tar:
            for member in tar.getmembers():
                target=canonical_child(staging,member.name)
                if member.issym() or member.islnk() or member.isdev(): raise HermesError("unsafe backup member")
                if member.isdir(): target.mkdir(parents=True,exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True,exist_ok=True)
                    source=tar.extractfile(member)
                    if source is None: raise HermesError("invalid backup member")
                    with source,target.open("wb") as output: shutil.copyfileobj(source,output)
                    os.chmod(target,member.mode & 0o700)
                else: raise HermesError("unsupported backup member")
        os.replace(staging,destination); fsync_dir(destination.parent)
        return {"profile":manifest["profile"],"restored_to":str(destination),"rehearsal":True}
    except Exception:
        raise
    finally: plain.unlink(missing_ok=True); shutil.rmtree(staging,ignore_errors=True)


def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True); b=sub.add_parser("backup"); b.add_argument("--profile",required=True); b.add_argument("--source",type=Path,required=True); b.add_argument("--output",type=Path,required=True); b.add_argument("--encryptor",type=Path,required=True); b.add_argument("--snapshotter",type=Path,required=True); r=sub.add_parser("restore"); r.add_argument("--archive",type=Path,required=True); r.add_argument("--manifest",type=Path,required=True); r.add_argument("--destination",type=Path,required=True); r.add_argument("--decryptor",type=Path,required=True); a=p.parse_args()
 try: value=backup(a.profile,a.source,a.output,a.encryptor,a.snapshotter) if a.command=="backup" else restore(a.archive,a.manifest,a.destination,a.decryptor); print(json.dumps(value,sort_keys=True)); return 0
 except HermesError as e: print(json.dumps({"error":str(e)})); return 2
if __name__=="__main__": raise SystemExit(main())
