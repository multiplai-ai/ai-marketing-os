#!/usr/bin/env python3
"""Validate value-only SOP bindings and pinned core locks."""
import argparse,re
from pathlib import Path
import yaml
FORBIDDEN={"steps","procedure","instructions","runbook"}
SHA=re.compile(r"^[0-9a-f]{40}$")
DIGEST=re.compile(r"^sha256:[0-9a-f]{64}$")
def main():
 p=argparse.ArgumentParser(); p.add_argument("path",type=Path); p.add_argument("--core-lock",action="store_true"); a=p.parse_args(); d=yaml.safe_load(a.path.read_text()) or {}
 if a.core_lock:
  core=d.get("core",{}); sops=d.get("sops")
  ok=(set(d)=={"core","sops"} and set(core)=={"version","commit","digest"}
      and SHA.fullmatch(str(core.get("commit",""))) and DIGEST.fullmatch(str(core.get("digest","")))
      and isinstance(sops,list) and len(sops)==len(set(sops)))
 else:
  ok=(d.get("schema_version")==1 and bool(d.get("sop_id")) and bool(d.get("entity"))
      and isinstance(d.get("values"),dict) and not (FORBIDDEN & set(d)))
 if not ok: print(f"invalid: {a.path}"); return 1
 print(f"valid: {a.path}"); return 0
if __name__=="__main__": raise SystemExit(main())
