"""`oya audit list` / `oya audit show N` — display audit log entries."""

import json
import sys

from .. import config
from ..audit.log import read_entries


def _list(args) -> int:
    entries = read_entries(config.audit_log_path())
    if not entries:
        print("(no entries)")
        return 0

    print(f"{'#':>3}  {'TIMESTAMP':<27}  {'WHO':<5}  {'ACTION':<10}  MESSAGE")
    for i, e in enumerate(entries, start=1):
        msg = e.get("message", "")
        if len(msg) > 60:
            msg = msg[:57] + "..."
        print(
            f"{i:>3}  {e.get('timestamp', '')[:26]:<27}  "
            f"{e.get('operator_type', '?'):<5}  "
            f"{e.get('action', ''):<10}  {msg}"
        )
    return 0


def _show(args) -> int:
    entries = read_entries(config.audit_log_path())
    n = args.line
    if n < 1 or n > len(entries):
        print(f"error: line {n} out of range (1..{len(entries)})", file=sys.stderr)
        return 1
    print(json.dumps(entries[n - 1], indent=2, sort_keys=True))
    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("audit", help="inspect the audit log")
    sub = p.add_subparsers(dest="audit_cmd", required=True)

    p_list = sub.add_parser("list", help="list all entries")
    p_list.set_defaults(func=_list)

    p_show = sub.add_parser("show", help="show one entry in full")
    p_show.add_argument("line", type=int, help="1-indexed line number")
    p_show.set_defaults(func=_show)
