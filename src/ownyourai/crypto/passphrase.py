"""`crypto/passphrase.py` — Passphrase resolution for encrypted private keys."""

import getpass
import os


def resolve_passphrase(priv_pem: bytes, *, no_passphrase: bool = False) -> bytes | None:
    """Detect key encryption and return the passphrase bytes, or None.

    Resolution order:
    1. no_passphrase=True → None (skip all prompts; for CI/testing)
    2. Key is not encrypted → None (detected by attempting unencrypted load)
    3. OWNYOURAI_PASSPHRASE env var is set → use it (empty string = None)
    4. Fallback → interactive getpass prompt

    Args:
        priv_pem: Raw PEM bytes of the private key.
        no_passphrase: If True, return None without any detection or prompting.

    Returns:
        Passphrase as bytes, or None if no passphrase is needed/provided.
    """
    if no_passphrase:
        return None

    # Detect key encryption from PEM headers — avoids ValueError conflation.
    # PKCS8 encrypted keys contain the marker "ENCRYPTED PRIVATE KEY" in their header.
    # Legacy SEC1/traditional encrypted keys contain "Proc-Type: 4,ENCRYPTED".
    # Unencrypted PKCS8 keys have "BEGIN PRIVATE KEY" with no "ENCRYPTED" prefix.
    is_encrypted = b"ENCRYPTED PRIVATE KEY" in priv_pem or b"Proc-Type: 4,ENCRYPTED" in priv_pem
    if not is_encrypted:
        return None  # plaintext key — no passphrase needed

    # Try environment variable
    env = os.environ.get("OWNYOURAI_PASSPHRASE")
    if env is not None:
        return env.encode() if env else None

    # Interactive prompt
    phrase = getpass.getpass("Passphrase: ")
    return phrase.encode() if phrase else None
