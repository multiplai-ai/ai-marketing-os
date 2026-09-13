#!/usr/bin/env python3
"""Transactional writer fencing and external-effect idempotency ledger."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import stat
import time
from pathlib import Path

from hermes_common import HermesError, require_id

STATES = ("prepared", "submitting", "submitted", "provider-confirmed", "failed")


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.is_symlink() or path.is_symlink() or path.parent.resolve()!=path.parent.absolute(): raise HermesError("unsafe writer ledger path")
    parent_stat=path.parent.stat()
    if parent_stat.st_uid!=os.geteuid() or stat.S_IMODE(parent_stat.st_mode)&0o077: raise HermesError("writer ledger directory must be private and owned by broker")
    descriptor=os.open(path,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600); os.close(descriptor)
    file_stat=path.stat()
    if not stat.S_ISREG(file_stat.st_mode) or file_stat.st_uid!=os.geteuid() or stat.S_IMODE(file_stat.st_mode)&0o077: raise HermesError("writer ledger must be private and owned by broker")
    db = sqlite3.connect(path, timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("pragma journal_mode=WAL")
    db.execute("pragma synchronous=FULL")
    db.execute("pragma foreign_keys=ON")
    db.executescript("""
      create table if not exists leases(
        profile text primary key, holder text not null, epoch integer not null,
        expires_at real not null, updated_at real not null);
      create table if not exists effects(
        profile text not null, action_type text not null, action_key text not null,
        credential_alias text not null,
        epoch integer not null, state text not null,
        provider_reference text, request_digest text not null,
        created_at real not null, updated_at real not null,
        primary key(profile, action_type, action_key));
    """)
    return db


def _tx(db: sqlite3.Connection):
    db.execute("BEGIN IMMEDIATE")


def acquire(db: sqlite3.Connection, profile: str, holder: str, ttl: int, now: float | None = None) -> int:
    require_id(profile, "profile"); require_id(holder, "holder")
    if ttl < 1 or ttl > 3600: raise HermesError("lease TTL outside 1..3600 seconds")
    now = time.time() if now is None else now
    _tx(db)
    try:
        row = db.execute("select * from leases where profile=?", (profile,)).fetchone()
        if row and row["expires_at"] > now and row["holder"] != holder:
            raise HermesError("WRITER_LEASE_HELD")
        # Every takeover and every post-expiry reacquisition advances the fence,
        # including reuse of the same textual holder identity by a new process.
        epoch = (row["epoch"] + 1) if row and (row["holder"] != holder or row["expires_at"] <= now) else (row["epoch"] if row else 1)
        db.execute("insert into leases values(?,?,?,?,?) on conflict(profile) do update set holder=excluded.holder, epoch=excluded.epoch, expires_at=excluded.expires_at, updated_at=excluded.updated_at", (profile, holder, epoch, now + ttl, now))
        db.commit(); return epoch
    except Exception:
        db.rollback(); raise


def _fence(db: sqlite3.Connection, profile: str, holder: str, epoch: int, now: float) -> None:
    row = db.execute("select * from leases where profile=?", (profile,)).fetchone()
    if not row or row["holder"] != holder or row["epoch"] != epoch or row["expires_at"] <= now:
        raise HermesError("STALE_WRITER_FENCE")


def release(db: sqlite3.Connection, profile: str, holder: str, epoch: int,
            now: float | None = None) -> int:
    """Surrender the active lease while retaining its epoch as audit evidence."""
    now = time.time() if now is None else now
    _tx(db)
    try:
        _fence(db, profile, holder, epoch, now)
        db.execute(
            "update leases set expires_at=?, updated_at=? where profile=?",
            (now, now, profile),
        )
        db.commit()
        return epoch
    except Exception:
        db.rollback()
        raise


def renew(db: sqlite3.Connection, profile: str, holder: str, epoch: int, ttl: int,
          now: float | None = None) -> int:
    if ttl < 1 or ttl > 3600: raise HermesError("lease TTL outside 1..3600 seconds")
    now=time.time() if now is None else now
    _tx(db)
    try:
        _fence(db,profile,holder,epoch,now)
        db.execute("update leases set expires_at=?, updated_at=? where profile=?",(now+ttl,now,profile))
        db.commit(); return epoch
    except Exception:
        db.rollback(); raise


def prepare(db: sqlite3.Connection, profile: str, holder: str, epoch: int,
            action_type: str, action_key: str, credential_alias: str,
            request_digest: str,
            now: float | None = None) -> dict:
    now = time.time() if now is None else now
    require_id(action_type, "action type"); require_id(action_key, "action key"); require_id(credential_alias, "credential alias")
    _tx(db)
    try:
        _fence(db, profile, holder, epoch, now)
        prior = db.execute("select * from effects where profile=? and action_type=? and action_key=?", (profile, action_type, action_key)).fetchone()
        if prior:
            if prior["request_digest"] != request_digest: raise HermesError("IDEMPOTENCY_KEY_REUSED")
            db.commit(); return dict(prior)
        db.execute("insert into effects values(?,?,?,?,?,?,?,?,?,?)", (profile, action_type, action_key, credential_alias, epoch, "prepared", None, request_digest, now, now))
        db.commit(); return lookup(db, profile, action_type, action_key)
    except Exception:
        db.rollback(); raise


def transition(db: sqlite3.Connection, profile: str, holder: str, epoch: int,
               action_type: str, action_key: str, target: str,
               provider_reference: str | None = None,
               now: float | None = None) -> dict:
    if target not in STATES: raise HermesError("invalid effect state")
    now = time.time() if now is None else now
    allowed = {"prepared": {"submitting", "failed"}, "submitting": {"submitted", "provider-confirmed", "failed"}, "submitted": {"provider-confirmed", "failed"}, "provider-confirmed": set(), "failed": set()}
    _tx(db)
    try:
        _fence(db, profile, holder, epoch, now)
        row = db.execute("select * from effects where profile=? and action_type=? and action_key=?", (profile, action_type, action_key)).fetchone()
        if not row: raise HermesError("EFFECT_NOT_PREPARED")
        if target == row["state"]:
            db.commit(); return dict(row)
        if target not in allowed[row["state"]]: raise HermesError("INVALID_EFFECT_TRANSITION")
        if target == "provider-confirmed" and not provider_reference: raise HermesError("provider reference required")
        db.execute("update effects set state=?, provider_reference=coalesce(?,provider_reference), updated_at=? where profile=? and action_type=? and action_key=?", (target, provider_reference, now, profile, action_type, action_key))
        db.commit(); return lookup(db, profile, action_type, action_key)
    except Exception:
        db.rollback(); raise


def lookup(db: sqlite3.Connection, profile: str, action_type: str, action_key: str) -> dict | None:
    row = db.execute("select * from effects where profile=? and action_type=? and action_key=?", (profile, action_type, action_key)).fetchone()
    return dict(row) if row else None


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--db", type=Path, required=True); p.add_argument("--profile", required=True)
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("acquire"); a.add_argument("--holder", required=True); a.add_argument("--ttl", type=int, default=300)
    rel = sub.add_parser("release"); rel.add_argument("--holder", required=True); rel.add_argument("--epoch", type=int, required=True)
    prep = sub.add_parser("prepare"); prep.add_argument("--holder", required=True); prep.add_argument("--epoch", type=int, required=True); prep.add_argument("--action-type", required=True); prep.add_argument("--key", required=True); prep.add_argument("--credential-alias", required=True); prep.add_argument("--request-digest", required=True)
    trans = sub.add_parser("transition"); trans.add_argument("--holder", required=True); trans.add_argument("--epoch", type=int, required=True); trans.add_argument("--action-type", required=True); trans.add_argument("--key", required=True); trans.add_argument("--state", required=True); trans.add_argument("--provider-reference")
    look = sub.add_parser("lookup"); look.add_argument("--action-type", required=True); look.add_argument("--key", required=True)
    args = p.parse_args(); db = connect(args.db)
    try:
        if args.command == "acquire": value = {"epoch": acquire(db,args.profile,args.holder,args.ttl)}
        elif args.command == "release": value = {"released_epoch": release(db,args.profile,args.holder,args.epoch)}
        elif args.command == "prepare": value = prepare(db,args.profile,args.holder,args.epoch,args.action_type,args.key,args.credential_alias,args.request_digest)
        elif args.command == "transition": value = transition(db,args.profile,args.holder,args.epoch,args.action_type,args.key,args.state,args.provider_reference)
        else: value = lookup(db,args.profile,args.action_type,args.key)
        print(json.dumps(value,sort_keys=True)); return 0
    except HermesError as exc:
        print(json.dumps({"error":str(exc)},sort_keys=True)); return 2


if __name__ == "__main__": raise SystemExit(main())
