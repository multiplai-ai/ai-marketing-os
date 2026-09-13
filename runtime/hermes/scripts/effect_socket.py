#!/usr/bin/env python3
"""Socket-activated privileged boundary for approved provider effects."""
from __future__ import annotations

import argparse
import json
import os
import pwd
import socket
import struct
from pathlib import Path

from hermes_common import HermesError, require_id
import effect_broker
import writer_lease


def handle(request: dict, peer_uid: int, expected_uid: int, profile: str,
           db_path: Path, verifier: Path, adapter: Path, state_root: Path) -> dict:
    require_id(profile,"profile")
    if peer_uid!=expected_uid: raise HermesError("effect broker peer is not authorized for profile")
    holder=f"frontdoor-{profile}-{peer_uid}"
    db=writer_lease.connect(db_path); epoch=writer_lease.acquire(db,profile,holder,300)
    if isinstance(request,dict) and set(request)=={"plan","signature"}:
        return effect_broker.execute(db_path,holder,epoch,Path(request["plan"]),Path(request["signature"]),verifier,adapter,state_root)
    if isinstance(request,dict) and set(request)=={"action_type","idempotency_key"}:
        return effect_broker.recover(db_path,holder,epoch,profile,request["action_type"],request["idempotency_key"],verifier,adapter,state_root)
    raise HermesError("invalid effect broker request")


def serve(listener: socket.socket, profile: str, db_path: Path, verifier: Path,
          adapter: Path, state_root: Path) -> None:
    expected=pwd.getpwnam(f"hermes-frontdoor-{profile}").pw_uid
    while True:
        connection,_=listener.accept()
        with connection:
            try:
                connection.settimeout(5)
                peer=struct.unpack("3i",connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize("3i")))[1]
                chunks=[]; size=0
                while True:
                    chunk=connection.recv(min(4096,65537-size))
                    if not chunk: raise HermesError("effect broker request ended before newline")
                    chunks.append(chunk); size+=len(chunk)
                    if size>65536: raise HermesError("effect broker request is too large")
                    if b"\n" in chunk: break
                raw=b"".join(chunks)
                line,remainder=raw.split(b"\n",1)
                if remainder: raise HermesError("effect broker accepts one framed request per connection")
                result=handle(json.loads(line),peer,expected,profile,db_path,verifier,adapter,state_root)
            except (HermesError,KeyError,ValueError,json.JSONDecodeError,TimeoutError,socket.timeout) as exc:
                result={"error":str(exc)}
            try: connection.sendall((json.dumps(result,sort_keys=True)+"\n").encode())
            except (BrokenPipeError,TimeoutError,socket.timeout): pass


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--profile",required=True); p.add_argument("--db",type=Path,required=True); p.add_argument("--approval-verifier",type=Path,required=True); p.add_argument("--adapter",type=Path,required=True); p.add_argument("--state-root",type=Path,required=True); a=p.parse_args()
    try:
        if int(os.environ.get("LISTEN_FDS","0"))!=1: raise HermesError("effect broker requires exactly one systemd socket")
        listener=socket.socket(fileno=3); serve(listener,a.profile,a.db,a.approval_verifier,a.adapter,a.state_root); return 0
    except (HermesError,KeyError,ValueError) as exc:
        os.write(2,(json.dumps({"error":str(exc)},sort_keys=True)+"\n").encode()); return 2


if __name__=="__main__": raise SystemExit(main())
