"""`oya verify` — verify signatures and hash chain integrity of the audit log."""

import sys

from .. import config
from ..audit.log import verify_log


def _load_pubkey(role: str) -> bytes | None:
    path = config.public_key_path(role)
    return path.read_bytes() if path.exists() else None


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
    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("verify", help="verify audit log signatures + hash chain")
    p.set_defaults(func=run)
