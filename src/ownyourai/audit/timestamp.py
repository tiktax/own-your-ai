"""
audit/timestamp.py — RFC 3161 Trusted Timestamp anchor for the audit log.

Usage: `oya audit anchor` (explicit opt-in — no automatic network calls).

The command hashes the entire audit.jsonl, submits the hash to a free TSA
(default: freetsa.org), and stores the DER-encoded TimeStampToken locally in
~/.ownyourai/timestamps.jsonl.

Verification (manual, requires openssl):
    openssl ts -reply -in <token.der> -text
    openssl ts -verify -data audit.jsonl -in <token.der> -CAfile freetsa_cacert.pem

Why opt-in:
    own-your-ai is offline-first. The user explicitly decides when to anchor.
    Typical usage: anchor once before handing an audit log to an auditor.
"""

import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

# SHA-256 AlgorithmIdentifier DER:
# SEQUENCE { OID 2.16.840.1.101.3.4.2.1, NULL }
# Bytes: 30 0d  06 09 60 86 48 01 65 03 04 02 01  05 00
_SHA256_ALG = bytes.fromhex("300d0609608648016503040201" "0500")


class TimestampError(Exception):
    """Raised when the TSA request fails or returns an unexpected response."""


def _build_ts_req(message_hash: bytes) -> bytes:
    """Build a minimal RFC 3161 TimeStampReq DER structure.

    Structure (ASN.1):
        TimeStampReq ::= SEQUENCE {
            version        INTEGER v1,
            messageImprint MessageImprint,
            nonce          INTEGER (random 8 bytes)
        }
        MessageImprint ::= SEQUENCE {
            hashAlgorithm  AlgorithmIdentifier,  -- SHA-256
            hashedMessage  OCTET STRING          -- 32 bytes
        }

    All inner lengths fit in one byte (< 128), so no long-form DER needed.
    """
    if len(message_hash) != 32:
        raise ValueError(f"Expected 32-byte SHA-256 hash, got {len(message_hash)} bytes")

    # OCTET STRING: tag 0x04, length 0x20 (32), then the hash
    hash_octet = b"\x04\x20" + message_hash  # 34 bytes

    # MessageImprint body = AlgorithmIdentifier (15 bytes) + OCTET STRING (34 bytes) = 49 bytes
    mi_body = _SHA256_ALG + hash_octet
    msg_imprint = b"\x30" + bytes([len(mi_body)]) + mi_body  # SEQUENCE, 51 bytes total

    # version INTEGER v1: tag 0x02, length 0x01, value 0x01
    version = b"\x02\x01\x01"  # 3 bytes

    # Nonce: random 8 bytes, strip leading zeros to avoid negative-integer DER encoding
    nonce_val = os.urandom(8).lstrip(b"\x00") or b"\x01"
    nonce = b"\x02" + bytes([len(nonce_val)]) + nonce_val  # 2–10 bytes

    body = version + msg_imprint + nonce
    if len(body) > 127:
        raise RuntimeError(f"TimeStampReq body too long for single-byte DER: {len(body)}")

    return b"\x30" + bytes([len(body)]) + body


def anchor(log_path: Path, ts_store_path: Path, tsa_url: str) -> dict:
    """Hash audit.jsonl, send to TSA, and save the TimeStampToken locally.

    Args:
        log_path: Path to audit.jsonl.
        ts_store_path: Where to append the token record (timestamps.jsonl).
        tsa_url: HTTP endpoint of the TSA (must accept RFC 3161 POST requests).

    Returns:
        The token record dict that was saved to ts_store_path.

    Raises:
        TimestampError: On TSA connection failure or invalid response.
    """
    content = log_path.read_bytes()
    log_hash_bytes = hashlib.sha256(content).digest()
    log_hash_hex = log_hash_bytes.hex()

    entry_count = sum(1 for ln in content.decode(errors="replace").splitlines() if ln.strip())

    ts_req = _build_ts_req(log_hash_bytes)

    req = urllib.request.Request(
        tsa_url,
        data=ts_req,
        headers={"Content-Type": "application/timestamp-query"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            ts_resp = resp.read()
    except urllib.error.URLError as exc:
        raise TimestampError(f"Cannot connect to TSA at {tsa_url}: {exc}") from exc

    if not ts_resp:
        raise TimestampError("TSA returned an empty response")

    token: dict = {
        "anchored_at": datetime.now(UTC).isoformat(),
        "log_hash": log_hash_hex,
        "log_entry_count": entry_count,
        "tsa_url": tsa_url,
        "token_hex": ts_resp.hex(),
    }

    ts_store_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Pre-create with 0o600 before writing so the file is never world-readable.
    # (open("a") alone would create with umask-default 0o644 first.)
    if not ts_store_path.exists():
        ts_store_path.touch(mode=0o600)
    with ts_store_path.open("a") as f:
        f.write(json.dumps(token) + "\n")

    return token
