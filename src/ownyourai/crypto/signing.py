"""
signing.py — ECDSA operation log signing and verification

Design:
    - AI key pair:    ai_private_key.pem / ai_public_key.pem
    - Human key pair: human_private_key.pem / human_public_key.pem

    Separating keys makes operator_type technically verifiable:
    the key_fingerprint field in each log entry identifies which
    public key was used, proving whether the operation was AI or human.

Algorithm: NIST P-256 with SHA-256 (deterministic ECDSA per RFC 6979)

Inherited from ai-infra-portfolio Phase 5 (tools/trustless_audit/src/signing.py).
"""

import hashlib
import json
from datetime import UTC, datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


def _load_private_key(private_key_pem: bytes, password: bytes | None = None):
    return serialization.load_pem_private_key(private_key_pem, password=password)


def _load_public_key(public_key_pem: bytes):
    return serialization.load_pem_public_key(public_key_pem)


def _key_fingerprint(public_key_pem: bytes) -> str:
    return hashlib.sha256(public_key_pem).hexdigest()


def _canonical_payload(log_entry: dict) -> bytes:
    """Stable JSON serialization for signing (sorted keys, no whitespace)."""
    entry_copy = {k: v for k, v in log_entry.items() if k not in ("signature", "key_fingerprint")}
    return json.dumps(entry_copy, sort_keys=True, separators=(",", ":")).encode()


def generate_keypair() -> tuple[bytes, bytes]:
    """Generate a new ECDSA P-256 keypair and return (private_pem, public_pem)."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def sign_operation_log(log_entry: dict, private_key_pem: bytes) -> dict:
    """
    Sign an operation log entry with ECDSA P-256.

    Returns log_entry with 'signature' (hex) and 'key_fingerprint' (sha256 of pubkey) added.
    """
    if "timestamp" not in log_entry:
        log_entry = {**log_entry, "timestamp": datetime.now(UTC).isoformat()}

    private_key = _load_private_key(private_key_pem)
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    payload = _canonical_payload(log_entry)
    signature_der = private_key.sign(payload, ec.ECDSA(hashes.SHA256()))

    return {
        **log_entry,
        "signature": signature_der.hex(),
        "key_fingerprint": _key_fingerprint(public_key_pem),
    }


def verify_signature(signed_log: dict, public_key_pem: bytes) -> bool:
    """Verify ECDSA signature on a signed log entry."""
    if "signature" not in signed_log:
        return False

    try:
        public_key = _load_public_key(public_key_pem)
        payload = _canonical_payload(signed_log)
        signature_der = bytes.fromhex(signed_log["signature"])
        public_key.verify(signature_der, payload, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError):
        return False


def identify_operator_type(
    signed_log: dict, ai_public_key_pem: bytes, human_public_key_pem: bytes
) -> str:
    """Determine operator type by matching key_fingerprint. Returns 'AI', 'HUMAN', or 'UNKNOWN'."""
    if "key_fingerprint" not in signed_log:
        return "UNKNOWN"

    fp = signed_log["key_fingerprint"]

    if fp == _key_fingerprint(ai_public_key_pem):
        return "AI"
    elif fp == _key_fingerprint(human_public_key_pem):
        return "HUMAN"
    else:
        return "UNKNOWN"
