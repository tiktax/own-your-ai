"""
identity/did.py — did:key stub.

Phase 1 implements only did:key derivation from an ECDSA P-256 public key.
did:web, did:peer, did:ion are deferred to Phase 2.

See docs/decisions/0002-did-method-deferred.md
"""

import base64
import hashlib

from cryptography.hazmat.primitives import serialization

# Multicodec prefix for P-256 public key: 0x1200
_P256_MULTICODEC_PREFIX = b"\x80\x24"


def derive_did_key(public_key_pem: bytes) -> str:
    """
    Derive a did:key identifier from an ECDSA P-256 public key (PEM).

    This is a stub implementation: it concatenates a multicodec prefix
    with the raw public key bytes and encodes as multibase (base58btc 'z' prefix
    is the formal spec; we use base64url 'u' here for simplicity in Phase 1).

    A formal did:key implementation will replace this in Phase 2.
    """
    pub = serialization.load_pem_public_key(public_key_pem)
    raw = pub.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint,
    )
    payload = _P256_MULTICODEC_PREFIX + raw
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    return f"did:key:u{encoded}"


def fingerprint(public_key_pem: bytes) -> str:
    """Short, human-readable identifier (first 16 hex chars of sha256)."""
    return hashlib.sha256(public_key_pem).hexdigest()[:16]
