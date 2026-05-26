"""
audit/log.py — Append-only personal AI audit log with ECDSA signatures and hash chain.

Format: JSON Lines. Each entry has:
    timestamp, operator_type (AI|HUMAN), action, message, prev_hash,
    signature, key_fingerprint

Hash chain: each entry's prev_hash references the sha256 of the previous line
(canonical JSON). The first entry has prev_hash = "GENESIS".

Inherited (simplified) from ai-infra-portfolio Phase 5 (tools/trustless_audit/src/audit.py).
Differences from upstream:
    - No pre-signing legacy support: every entry is signed from line 1
    - No multisig / WORM / PQC dependencies
    - Hash chain (prev_hash) added for tamper detection without external storage
    - Paths come from ownyourai.config, not hardcoded ITIL5 paths
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from ..crypto.signing import (
    identify_operator_type,
    sign_operation_log,
    verify_signature,
)

GENESIS = "GENESIS"


def _hash_line(line: str) -> str:
    return hashlib.sha256(line.encode()).hexdigest()


def _last_hash(log_path: Path) -> str:
    if not log_path.exists() or log_path.stat().st_size == 0:
        return GENESIS
    last_line = ""
    with log_path.open("r") as f:
        for line in f:
            line = line.strip()
            if line:
                last_line = line
    return _hash_line(last_line) if last_line else GENESIS


def append_entry(
    log_path: Path,
    *,
    message: str,
    operator_type: str,
    private_key_pem: bytes,
    action: str = "log",
) -> dict:
    """Sign and append a new entry to the audit log. Returns the signed entry."""
    if operator_type not in ("AI", "HUMAN"):
        raise ValueError(f"operator_type must be 'AI' or 'HUMAN', got {operator_type!r}")

    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "operator_type": operator_type,
        "action": action,
        "message": message,
        "prev_hash": _last_hash(log_path),
    }
    signed = sign_operation_log(entry, private_key_pem)

    with log_path.open("a") as f:
        f.write(json.dumps(signed, sort_keys=True, separators=(",", ":")) + "\n")

    return signed


def read_entries(log_path: Path) -> list[dict]:
    """Read all entries from the log."""
    if not log_path.exists():
        return []
    entries: list[dict] = []
    for line in log_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def verify_log(
    log_path: Path,
    *,
    ai_public_key_pem: bytes | None,
    human_public_key_pem: bytes | None,
) -> dict:
    """
    Verify signatures AND hash chain integrity for every entry in the log.

    Returns:
        {
            total: int,
            ai_ops: int,
            human_ops: int,
            signature_failures: list[int],   # 1-indexed line numbers
            chain_breaks: list[int],         # 1-indexed line numbers
            tampering_detected: bool,
        }
    """
    result = {
        "total": 0,
        "ai_ops": 0,
        "human_ops": 0,
        "signature_failures": [],
        "chain_breaks": [],
        "tampering_detected": False,
    }
    if not log_path.exists():
        return result

    prev_hash = GENESIS
    with log_path.open("r") as f:
        lines = [ln for ln in (line.strip() for line in f) if ln]

    for i, raw_line in enumerate(lines, start=1):
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError:
            result["chain_breaks"].append(i)
            continue

        result["total"] += 1

        if entry.get("prev_hash") != prev_hash:
            result["chain_breaks"].append(i)

        verified = False
        if ai_public_key_pem and verify_signature(entry, ai_public_key_pem):
            verified = True
            result["ai_ops"] += 1
        elif human_public_key_pem and verify_signature(entry, human_public_key_pem):
            verified = True
            result["human_ops"] += 1

        if not verified:
            result["signature_failures"].append(i)

        # Confirm declared operator_type matches the key actually used
        if (
            verified
            and ai_public_key_pem
            and human_public_key_pem
            and identify_operator_type(entry, ai_public_key_pem, human_public_key_pem)
            != entry.get("operator_type")
        ):
            result["signature_failures"].append(i)

        prev_hash = _hash_line(raw_line)

    result["tampering_detected"] = bool(result["signature_failures"] or result["chain_breaks"])
    return result
