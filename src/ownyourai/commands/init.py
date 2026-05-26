"""`oya init` — generate human/ai keypairs and scaffold ~/.ownyourai/."""

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


def run(args) -> int:
    home = config.home_dir()
    keys = config.keys_dir()

    if home.exists() and any(home.iterdir()) and not getattr(args, "force", False):
        print(
            f"error: {home} already exists and is not empty. Re-run with --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    keys.mkdir(parents=True, exist_ok=True)

    for role in ("human", "ai"):
        priv_path = config.private_key_path(role)
        pub_path = config.public_key_path(role)
        private_pem, public_pem = generate_keypair()
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
    print(f"  audit log: {config.audit_log_path()} (will be created on first sign)")
    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("init", help="initialize ~/.ownyourai/ with keypairs")
    p.add_argument("--force", action="store_true", help="overwrite existing data")
    p.set_defaults(func=run)
