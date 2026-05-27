"""
identity/did.py — did:key derivation for ECDSA P-256 public keys.

Phase 2 implements spec-compliant did:key using base58btc multibase encoding.
did:web, did:peer, did:ion are deferred to a later phase.

See docs/decisions/0002-did-method-deferred.md
    docs/decisions/0006-did-key-base58btc.md
"""

import hashlib

import base58
from cryptography.hazmat.primitives import serialization

# Multicodec prefix for P-256 public key: 0x1200 encoded as unsigned varint → 0x80 0x24
_P256_MULTICODEC_PREFIX = b"\x80\x24"


def derive_did_key(public_key_pem: bytes) -> str:
    """
    Derive a did:key identifier from an ECDSA P-256 public key (PEM).

    Encoding: multicodec prefix (0x1200) + compressed P-256 point,
    encoded as multibase base58btc ('z' prefix) per W3C DID Core spec.
    """
    pub = serialization.load_pem_public_key(public_key_pem)
    raw = pub.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint,
    )
    payload = _P256_MULTICODEC_PREFIX + raw
    encoded = base58.b58encode(payload).decode()
    return f"did:key:z{encoded}"


def fingerprint(public_key_pem: bytes) -> str:
    """Short, human-readable identifier (first 16 hex chars of sha256)."""
    return hashlib.sha256(public_key_pem).hexdigest()[:16]
