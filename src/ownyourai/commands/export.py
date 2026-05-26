"""`oya export` — export the audit log as portable JSON (GDPR Art.20 minimal form)."""

import json
from datetime import UTC, datetime

from .. import __version__, config
from ..audit.log import read_entries


def run(args) -> int:
    entries = read_entries(config.audit_log_path())
    bundle = {
        "schema": "own-your-ai.export/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "tool_version": __version__,
        "entry_count": len(entries),
        "entries": entries,
    }
    print(json.dumps(bundle, indent=2, sort_keys=True))
    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("export", help="export audit log as portable JSON")
    p.set_defaults(func=run)
