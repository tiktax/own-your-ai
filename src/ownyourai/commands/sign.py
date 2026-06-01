"""`oya sign` — sign a message and append it to the audit log."""

import sys

from .. import config
from ..audit.log import append_entry
from ..crypto.passphrase import resolve_passphrase


def run(args) -> int:
    role = args.as_role
    priv_path = config.private_key_path(role)
    if not priv_path.exists():
        print(
            f"error: private key not found at {priv_path}. Run `oya init` first.",
            file=sys.stderr,
        )
        return 1

    priv_pem = priv_path.read_bytes()
    passphrase = resolve_passphrase(priv_pem, no_passphrase=getattr(args, "no_passphrase", False))

    entry = append_entry(
        config.audit_log_path(),
        message=args.message,
        operator_type=role.upper(),
        private_key_pem=priv_pem,
        action=args.action,
        passphrase=passphrase,
    )

    print(f"signed entry appended ({role.upper()})")
    print(f"  timestamp:        {entry['timestamp']}")
    print(f"  key_fingerprint:  {entry['key_fingerprint'][:32]}...")
    print(f"  prev_hash:        {entry['prev_hash'][:32]}...")
    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("sign", help="sign a message and append to audit log")
    p.add_argument("--message", "-m", required=True, help="message to sign")
    p.add_argument(
        "--as",
        dest="as_role",
        choices=("human", "ai"),
        default="human",
        help="signing identity (default: human)",
    )
    p.add_argument("--action", default="log", help="action label (default: log)")
    p.add_argument(
        "--no-passphrase",
        action="store_true",
        dest="no_passphrase",
        help="skip passphrase prompt (for unencrypted keys)",
    )
    p.set_defaults(func=run)
