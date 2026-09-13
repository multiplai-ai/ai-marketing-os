#!/usr/bin/env python3
"""Detect client/entity names that must move from core SOPs to bindings."""
import argparse,re
from pathlib import Path
SOP_TERMS=("VuMedi","Yeager","MultiplAI","Marketer in the Loop","MITL","Proof","AirOps","Growth Assistant","GT Schools","Pinckney Harmon","Hanna Huffman")
TOOL_TERMS=("VuMedi","Yeager","Proof","AirOps","Growth Assistant","GT Schools","Pinckney Harmon","Hanna Huffman")
def contains_term(value,term):
 # Standard title-case marketing terminology is not a client identifier.
 # Keep bare capitalized Proof blocked; do not rewrite useful methodology.
 if term=="Proof":
  value=re.sub(r"\b(?:Social Proof|Types of Proof|Other Proof|Matching Proof to Claims|Proof Points?|Proof Inventory|Proof Gaps|Proof Mapping)\b", "", value)
 flags=0 if term=="Proof" else re.I
 return re.search(rf"\b{re.escape(term)}\b",value,flags) is not None
def main():
 p=argparse.ArgumentParser(); p.add_argument("root",type=Path); a=p.parse_args(); hits=[]
 files=[(f,SOP_TERMS) for f in (a.root/"sops").rglob("*")] + [(f,TOOL_TERMS) for f in (a.root/"tools").rglob("*")]
 for f,terms in sorted(files,key=lambda item:str(item[0])):
  if f.name == "check_client_scrub.py": continue
  for term in terms:
   if contains_term(f.name,term): hits.append(f"{f.relative_to(a.root)}: path contains {term}")
  if f.is_file() and f.suffix.lower() in {".md",".yaml",".yml",".py"}:
   text=f.read_text(errors="replace")
   for term in terms:
    if contains_term(text,term): hits.append(f"{f.relative_to(a.root)}: {term}")
 if hits: print("\n".join(hits)); return 1
 print("client scrub: pass"); return 0
if __name__=="__main__": raise SystemExit(main())
