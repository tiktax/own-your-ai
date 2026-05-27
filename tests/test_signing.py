"""Tests for ownyourai.crypto.signing."""

from ownyourai.crypto.signing import (
    generate_keypair,
    identify_operator_type,
    sign_operation_log,
    verify_signature,
)


def test_sign_and_verify_roundtrip():
    priv, pub = generate_keypair()
    signed = sign_operation_log({"action": "test", "data": "hello"}, priv)
    assert verify_signature(signed, pub) is True


def test_verify_rejects_tampered_payload():
    priv, pub = generate_keypair()
    signed = sign_operation_log({"action": "test", "data": "hello"}, priv)
    signed["data"] = "tampered"
    assert verify_signature(signed, pub) is False


def test_verify_rejects_wrong_key():
    priv_a, _ = generate_keypair()
    _, pub_b = generate_keypair()
    signed = sign_operation_log({"action": "test"}, priv_a)
    assert verify_signature(signed, pub_b) is False


def test_identify_operator_type():
    ai_priv, ai_pub = generate_keypair()
    human_priv, human_pub = generate_keypair()

    ai_signed = sign_operation_log({"action": "x"}, ai_priv)
    human_signed = sign_operation_log({"action": "y"}, human_priv)

    assert identify_operator_type(ai_signed, ai_pub, human_pub) == "AI"
    assert identify_operator_type(human_signed, ai_pub, human_pub) == "HUMAN"


def test_identify_unknown_when_no_fingerprint():
    assert identify_operator_type({"action": "x"}, b"", b"") == "UNKNOWN"


def test_signature_is_deterministic_format():
    priv, _ = generate_keypair()
    signed = sign_operation_log({"action": "test"}, priv)
    # Signature is a hex string
    assert isinstance(signed["signature"], str)
    bytes.fromhex(signed["signature"])  # raises if not valid hex


def test_generate_keypair_with_passphrase():
    passphrase = b"s3cr3t"
    priv, pub = generate_keypair(passphrase=passphrase)
    # Encrypted PEM contains ENCRYPTED header
    assert b"ENCRYPTED" in priv
    # Signing with correct passphrase works
    signed = sign_operation_log({"action": "test"}, priv, passphrase=passphrase)
    assert verify_signature(signed, pub) is True


def test_generate_keypair_wrong_passphrase_fails():
    import pytest

    priv, _ = generate_keypair(passphrase=b"correct")
    with pytest.raises((ValueError, TypeError)):
        sign_operation_log({"action": "test"}, priv, passphrase=b"wrong")
