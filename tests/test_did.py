"""Tests for ownyourai.identity.did."""

import re

from ownyourai.crypto.signing import generate_keypair
from ownyourai.identity.did import derive_did_key


def test_did_key_z_prefix():
    _, pub = generate_keypair()
    did = derive_did_key(pub)
    assert did.startswith("did:key:z"), f"Expected did:key:z prefix, got: {did}"


def test_did_key_base58btc_charset():
    """Base58btc uses alphanumeric chars excluding 0, O, I, l."""
    _, pub = generate_keypair()
    did = derive_did_key(pub)
    encoded_part = did[len("did:key:z") :]
    assert re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]+", encoded_part), (
        f"Not valid base58btc: {encoded_part}"
    )


def test_did_key_is_deterministic():
    _, pub = generate_keypair()
    assert derive_did_key(pub) == derive_did_key(pub)


def test_different_keys_produce_different_dids():
    _, pub_a = generate_keypair()
    _, pub_b = generate_keypair()
    assert derive_did_key(pub_a) != derive_did_key(pub_b)
