"""Tests for ownyourai.audit.timestamp."""

import json
from unittest.mock import MagicMock, patch

import pytest

from ownyourai.audit.timestamp import TimestampError, _build_ts_req, anchor

# ---------------------------------------------------------------------------
# _build_ts_req unit tests
# ---------------------------------------------------------------------------

def test_build_ts_req_is_sequence():
    """Result starts with SEQUENCE tag 0x30."""
    req = _build_ts_req(b"\x00" * 32)
    assert req[0] == 0x30


def test_build_ts_req_length_range():
    """Total DER length should be 60–80 bytes for a 32-byte SHA-256 hash."""
    req = _build_ts_req(bytes(range(32)))
    assert 60 <= len(req) <= 80


def test_build_ts_req_contains_sha256_oid():
    """SHA-256 OID bytes must appear in the request."""
    sha256_oid = bytes.fromhex("0609608648016503040201")
    req = _build_ts_req(b"\xab" * 32)
    assert sha256_oid in req


def test_build_ts_req_contains_hash():
    """The 32-byte hash must appear verbatim in the request."""
    h = bytes(range(32))
    req = _build_ts_req(h)
    assert h in req


def test_build_ts_req_wrong_length():
    """Non-32-byte input raises ValueError."""
    with pytest.raises(ValueError, match="32-byte"):
        _build_ts_req(b"\x00" * 16)


def test_build_ts_req_nonce_varies():
    """Two requests for the same hash should differ (random nonce)."""
    h = b"\xff" * 32
    r1 = _build_ts_req(h)
    r2 = _build_ts_req(h)
    assert r1 != r2  # nonce differs


# ---------------------------------------------------------------------------
# anchor() integration tests (TSA mocked)
# ---------------------------------------------------------------------------

_FAKE_TOKEN = b"\x30\x10" + b"\x00" * 14  # minimal fake DER response


def _mock_urlopen(response_bytes: bytes):
    mock_resp = MagicMock()
    mock_resp.read.return_value = response_bytes
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_anchor_saves_token(tmp_path):
    """anchor() saves a token record to ts_store_path."""
    log_path = tmp_path / "audit.jsonl"
    log_path.write_text('{"test": "entry"}\n')
    ts_store = tmp_path / "timestamps.jsonl"

    with patch("urllib.request.urlopen", return_value=_mock_urlopen(_FAKE_TOKEN)):
        anchor(log_path, ts_store, "https://freetsa.org/tsr")

    assert ts_store.exists()
    saved = json.loads(ts_store.read_text().strip())
    assert saved["token_hex"] == _FAKE_TOKEN.hex()
    assert saved["log_entry_count"] == 1
    assert "anchored_at" in saved
    assert "log_hash" in saved


def test_anchor_raises_on_connection_error(tmp_path):
    """anchor() raises TimestampError on network failure."""
    import urllib.error

    log_path = tmp_path / "audit.jsonl"
    log_path.write_text('{"test": "entry"}\n')
    ts_store = tmp_path / "timestamps.jsonl"

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
        with pytest.raises(TimestampError, match="Cannot connect"):
            anchor(log_path, ts_store, "https://freetsa.org/tsr")


def test_anchor_raises_on_empty_response(tmp_path):
    """anchor() raises TimestampError when TSA returns empty bytes."""
    log_path = tmp_path / "audit.jsonl"
    log_path.write_text('{"test": "entry"}\n')
    ts_store = tmp_path / "timestamps.jsonl"

    with patch("urllib.request.urlopen", return_value=_mock_urlopen(b"")):
        with pytest.raises(TimestampError, match="empty response"):
            anchor(log_path, ts_store, "https://freetsa.org/tsr")


def test_anchor_file_permissions(tmp_path):
    """timestamps.jsonl is created with 0o600 permissions."""
    import stat

    log_path = tmp_path / "audit.jsonl"
    log_path.write_text('{"test": "entry"}\n')
    ts_store = tmp_path / "timestamps.jsonl"

    with patch("urllib.request.urlopen", return_value=_mock_urlopen(_FAKE_TOKEN)):
        anchor(log_path, ts_store, "https://freetsa.org/tsr")

    mode = stat.S_IMODE(ts_store.stat().st_mode)
    assert mode == 0o600
