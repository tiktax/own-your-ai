"""`oya init` — generate human/ai keypairs and scaffold ~/.ownyourai/."""

import getpass
import os
import sys

from .. import config
from ..crypto.signing import generate_keypair
from ..identity.did import derive_did_key

_CONFIG_TEMPLATE = """# own-your-ai configuration
# This file is created by `oya init` and is intentionally minimal in Phase 1.

[paths]
home = "{home}"
audit_log = "{audit_log}"

[identity]
# DID method used by `oya did show`. Only "key" is implemented in Phase 1.
did_method = "key"
"""


def _resolve_passphrase(no_passphrase: bool) -> bytes | None:
    """Return passphrase bytes or None (no encryption). Returns None on mismatch error."""
    if no_passphrase:
        return None
    env = os.environ.get("OWNYOURAI_PASSPHRASE")
    if env is not None:
        return env.encode() if env else None
    phrase = getpass.getpass("Passphrase for keys (empty = no encryption): ")
    if not phrase:
        print("warning: keys will be stored without passphrase encryption", file=sys.stderr)
        return None
    confirm = getpass.getpass("Confirm passphrase: ")
    if phrase != confirm:
        return _MISMATCH
    return phrase.encode()


_MISMATCH = object()


def run(args) -> int:
    home = config.home_dir()
    keys = config.keys_dir()

    if home.exists() and any(home.iterdir()) and not getattr(args, "force", False):
        print(
            f"error: {home} already exists and is not empty. Re-run with --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    passphrase_result = _resolve_passphrase(getattr(args, "no_passphrase", False))
    if passphrase_result is _MISMATCH:
        print("error: passphrases do not match", file=sys.stderr)
        return 1
    passphrase: bytes | None = passphrase_result  # type: ignore[assignment]

    home.mkdir(mode=0o700, parents=True, exist_ok=True)
    keys.mkdir(mode=0o700, parents=True, exist_ok=True)

    for role in ("human", "ai"):
        priv_path = config.private_key_path(role)
        pub_path = config.public_key_path(role)
        private_pem, public_pem = generate_keypair(passphrase=passphrase)
        priv_path.write_bytes(private_pem)
        priv_path.chmod(0o600)
        pub_path.write_bytes(public_pem)
        pub_path.chmod(0o644)
        did = derive_did_key(public_pem)
        print(f"  {role:5s}  did:key  {did}")

    config_path = config.config_path()
    config_path.write_text(_CONFIG_TEMPLATE.format(home=home, audit_log=config.audit_log_path()))

    print(f"\ninitialized: {home}")
    print(f"  keys:      {keys}")
    print(f"  encrypted: {'yes' if passphrase else 'no (--no-passphrase)'}")
    print(f"  audit log: {config.audit_log_path()} (will be created on first sign)")
    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("init", help="initialize ~/.ownyourai/ with keypairs")
    p.add_argument("--force", action="store_true", help="overwrite existing data")
    p.add_argument(
        "--no-passphrase",
        action="store_true",
        dest="no_passphrase",
        help="skip passphrase encryption (insecure; for testing/CI only)",
    )
    p.set_defaults(func=run)
