"""`oya verify` — verify signatures and hash chain integrity of the audit log."""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from .. import config
from ..audit.log import verify_log


def _load_pubkey(role: str) -> bytes | None:
    path = config.public_key_path(role)
    return path.read_bytes() if path.exists() else None


def _read_latest_anchor(ts_store: Path) -> tuple[dict | None, int]:
    """Return (most_recent_record, total_count) from timestamps.jsonl."""
    if not ts_store.exists():
        return None, 0
    last: dict | None = None
    count = 0
    for line in ts_store.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            last = json.loads(line)
            count += 1
        except json.JSONDecodeError:
            continue
    return last, count


def run(args) -> int:
    log_path = config.audit_log_path()
    if not log_path.exists():
        print(f"error: no audit log at {log_path}", file=sys.stderr)
        return 1

    report = verify_log(
        log_path,
        ai_public_key_pem=_load_pubkey("ai"),
        human_public_key_pem=_load_pubkey("human"),
    )

    print(f"audit log:  {log_path}")
    print(f"  total entries:        {report['total']}")
    print(f"  human ops:            {report['human_ops']}")
    print(f"  ai ops:               {report['ai_ops']}")
    print(f"  signature failures:   {len(report['signature_failures'])}")
    print(f"  chain breaks:         {len(report['chain_breaks'])}")

    if report["tampering_detected"]:
        print("\nWARNING tampering detected")
        if report["signature_failures"]:
            print(f"  signature failures at lines: {report['signature_failures']}")
        if report["chain_breaks"]:
            print(f"  chain breaks at lines:       {report['chain_breaks']}")
        return 2

    print("\nintegrity OK")

    ts_store = config.home_dir() / "timestamps.jsonl"
    anchor, anchor_count = _read_latest_anchor(ts_store)
    if anchor:
        tsa_host = urlparse(anchor.get("tsa_url", "")).hostname or anchor.get("tsa_url", "?")
        anchored_at = anchor.get("anchored_at", "")[:19] + "Z"
        log_entries = anchor.get("log_entry_count", "?")
        suffix = f"  [{anchor_count} tokens]" if anchor_count > 1 else ""
        print(f"Timestamp anchor:  {anchored_at}  ({log_entries} log entries, {tsa_host}){suffix}")
    else:
        print("Timestamp anchor:  none — run `oya audit anchor` to create one")

    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("verify", help="verify audit log signatures + hash chain")
    p.set_defaults(func=run)
