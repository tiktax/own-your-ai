"""`oya audit list` / `oya audit show N` / `oya audit summary` / `oya audit anchor`."""

import json
import sys

from .. import config
from ..audit.log import read_entries
from ..audit.timestamp import TimestampError
from ..audit.timestamp import anchor as ts_anchor

_DEFAULT_TSA_URL = "https://freetsa.org/tsr"


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


def _summary(args) -> int:
    """Print a human-readable statistics snapshot of the audit log."""
    entries = read_entries(config.audit_log_path())
    if not entries:
        print("No audit entries found. Run `oya sign` or `oya chat` first.")
        return 0

    total = len(entries)
    sessions = sum(1 for e in entries if e.get("action") == "chat_session")
    prompts = sum(1 for e in entries if e.get("action") == "chat_prompt")
    conversations = sessions + prompts

    first_ts = entries[0].get("timestamp", "")[:10]
    last_ts = entries[-1].get("timestamp", "")[:10]

    print(f"  {total:>4} total entries  |  {conversations:>3} conversations")
    print(f"       first: {first_ts}  |  last: {last_ts}")
    print()
    print("Run `oya verify` to check ECDSA signatures and hash-chain integrity.")
    return 0


def _anchor(args) -> int:
    """RFC 3161 timestamp-anchor the audit log via a Trusted Timestamping Authority."""
    log_path = config.audit_log_path()
    if not log_path.exists() or log_path.stat().st_size == 0:
        print(
            "error: audit log is empty or does not exist. "
            "Run `oya sign` or `oya chat` first.",
            file=sys.stderr,
        )
        return 1

    ts_store = config.home_dir() / "timestamps.jsonl"
    tsa_url: str = args.tsa_url

    print(f"Anchoring audit log via {tsa_url} ...")
    try:
        token = ts_anchor(log_path, ts_store, tsa_url)
    except TimestampError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"  anchored_at:   {token['anchored_at']}")
    print(f"  log_hash:      {token['log_hash'][:32]}...")
    print(f"  log_entries:   {token['log_entry_count']}")
    print(f"  token saved:   {ts_store}")
    print()
    print("To inspect the timestamp token:")
    print(
        "  python3 -c \"import json; t=json.loads(open('"
        + str(ts_store)
        + "').readlines()[-1]); "
        "open('/tmp/ts.der','wb').write(bytes.fromhex(t['token_hex']))\""
    )
    print("  openssl ts -reply -in /tmp/ts.der -text")
    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("audit", help="inspect the audit log")
    sub = p.add_subparsers(dest="audit_cmd", required=True)

    p_list = sub.add_parser("list", help="list all entries")
    p_list.set_defaults(func=_list)

    p_show = sub.add_parser("show", help="show one entry in full")
    p_show.add_argument("line", type=int, help="1-indexed line number")
    p_show.set_defaults(func=_show)

    p_summary = sub.add_parser("summary", help="show audit log statistics at a glance")
    p_summary.set_defaults(func=_summary)

    p_anchor = sub.add_parser(
        "anchor",
        help="RFC 3161 timestamp-anchor the audit log (requires internet, explicit opt-in)",
    )
    p_anchor.add_argument(
        "--tsa-url",
        dest="tsa_url",
        default=_DEFAULT_TSA_URL,
        help=f"TSA endpoint URL (default: {_DEFAULT_TSA_URL})",
    )
    p_anchor.set_defaults(func=_anchor)
