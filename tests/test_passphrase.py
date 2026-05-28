"""Tests for ownyourai.crypto.passphrase.resolve_passphrase."""


from ownyourai.crypto.passphrase import resolve_passphrase
from ownyourai.crypto.signing import generate_keypair


def test_no_passphrase_flag_returns_none():
    """no_passphrase=True → None, no detection, no prompt."""
    priv, _ = generate_keypair(passphrase=b"secret")
    result = resolve_passphrase(priv, no_passphrase=True)
    assert result is None


def test_unencrypted_key_returns_none():
    """Unencrypted key → None without prompting."""
    priv, _ = generate_keypair()  # no passphrase
    result = resolve_passphrase(priv)
    assert result is None


def test_encrypted_key_uses_env_var(monkeypatch):
    """Encrypted key + env var set → returns env var value."""
    priv, _ = generate_keypair(passphrase=b"mypass")
    monkeypatch.setenv("OWNYOURAI_PASSPHRASE", "mypass")
    result = resolve_passphrase(priv)
    assert result == b"mypass"


def test_encrypted_key_env_empty_returns_none(monkeypatch):
    """Encrypted key + OWNYOURAI_PASSPHRASE="" → None (no passphrase)."""
    priv, _ = generate_keypair(passphrase=b"mypass")
    monkeypatch.setenv("OWNYOURAI_PASSPHRASE", "")
    result = resolve_passphrase(priv)
    assert result is None


def test_encrypted_key_prompts_getpass(monkeypatch):
    """Encrypted key + no env var → calls getpass."""
    import getpass

    priv, _ = generate_keypair(passphrase=b"prompted")
    monkeypatch.delenv("OWNYOURAI_PASSPHRASE", raising=False)
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": "prompted")
    result = resolve_passphrase(priv)
    assert result == b"prompted"


def test_getpass_empty_returns_none(monkeypatch):
    """getpass returns empty string → None."""
    import getpass

    priv, _ = generate_keypair(passphrase=b"something")
    monkeypatch.delenv("OWNYOURAI_PASSPHRASE", raising=False)
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": "")
    result = resolve_passphrase(priv)
    assert result is None
