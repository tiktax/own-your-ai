"""Tests for ownyourai.audit.log."""

import json
from unittest.mock import MagicMock, patch

import pytest

from ownyourai.audit.log import (
    GENESIS,
    append_entry,
    read_entries,
    verify_log,
)
from ownyourai.crypto.signing import generate_keypair


@pytest.fixture
def keys():
    human_priv, human_pub = generate_keypair()
    ai_priv, ai_pub = generate_keypair()
    return {
        "human_priv": human_priv,
        "human_pub": human_pub,
        "ai_priv": ai_priv,
        "ai_pub": ai_pub,
    }


def test_append_and_read(tmp_path, keys):
    log = tmp_path / "audit.jsonl"
    e1 = append_entry(
        log, message="hello", operator_type="HUMAN", private_key_pem=keys["human_priv"]
    )
    e2 = append_entry(log, message="world", operator_type="AI", private_key_pem=keys["ai_priv"])

    entries = read_entries(log)
    assert len(entries) == 2
    assert entries[0]["message"] == "hello"
    assert entries[1]["message"] == "world"
    assert entries[0]["prev_hash"] == GENESIS
    assert entries[1]["prev_hash"] != GENESIS
    assert e1["operator_type"] == "HUMAN"
    assert e2["operator_type"] == "AI"


def test_verify_clean_log(tmp_path, keys):
    log = tmp_path / "audit.jsonl"
    append_entry(log, message="m1", operator_type="HUMAN", private_key_pem=keys["human_priv"])
    append_entry(log, message="m2", operator_type="AI", private_key_pem=keys["ai_priv"])

    report = verify_log(
        log, ai_public_key_pem=keys["ai_pub"], human_public_key_pem=keys["human_pub"]
    )
    assert report["tampering_detected"] is False
    assert report["total"] == 2
    assert report["human_ops"] == 1
    assert report["ai_ops"] == 1


def test_verify_detects_message_tampering(tmp_path, keys):
    log = tmp_path / "audit.jsonl"
    append_entry(log, message="original", operator_type="HUMAN", private_key_pem=keys["human_priv"])

    # Tamper: change the message field
    lines = log.read_text().splitlines()
    entry = json.loads(lines[0])
    entry["message"] = "tampered"
    log.write_text(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")

    report = verify_log(
        log, ai_public_key_pem=keys["ai_pub"], human_public_key_pem=keys["human_pub"]
    )
    assert report["tampering_detected"] is True
    assert 1 in report["signature_failures"]


def test_verify_detects_chain_break(tmp_path, keys):
    log = tmp_path / "audit.jsonl"
    append_entry(log, message="m1", operator_type="HUMAN", private_key_pem=keys["human_priv"])
    append_entry(log, message="m2", operator_type="HUMAN", private_key_pem=keys["human_priv"])
    append_entry(log, message="m3", operator_type="HUMAN", private_key_pem=keys["human_priv"])

    # Delete the middle entry — this should break the chain on line 2
    lines = log.read_text().splitlines()
    log.write_text(lines[0] + "\n" + lines[2] + "\n")

    report = verify_log(
        log, ai_public_key_pem=keys["ai_pub"], human_public_key_pem=keys["human_pub"]
    )
    assert report["tampering_detected"] is True
    assert 2 in report["chain_breaks"]


def test_invalid_operator_type_rejected(tmp_path, keys):
    log = tmp_path / "audit.jsonl"
    with pytest.raises(ValueError):
        append_entry(log, message="x", operator_type="ROBOT", private_key_pem=keys["human_priv"])


def test_read_entries_empty(tmp_path):
    log = tmp_path / "audit.jsonl"
    assert read_entries(log) == []


# ---------------------------------------------------------------------------
# oya audit summary subcommand tests
# ---------------------------------------------------------------------------


def test_audit_summary_shows_counts(tmp_path, keys, monkeypatch, capsys):
    """summary prints total entries and conversation count."""
    from ownyourai import cli, config

    monkeypatch.setenv("OWNYOURAI_HOME", str(tmp_path / "oya-home"))
    cli.main(["init", "--no-passphrase"])

    log = config.audit_log_path()
    append_entry(log, message="s1", operator_type="HUMAN", private_key_pem=keys["human_priv"],
                 action="chat_session")
    append_entry(log, message="p1", operator_type="HUMAN", private_key_pem=keys["human_priv"],
                 action="chat_prompt")
    append_entry(log, message="r1", operator_type="AI", private_key_pem=keys["ai_priv"],
                 action="chat_response")

    rc = cli.main(["audit", "summary"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "3" in out   # total entries
    assert "2" in out   # conversations (chat_session + chat_prompt)


def test_audit_summary_empty(tmp_path, monkeypatch, capsys):
    """summary with empty log prints a helpful message."""
    from ownyourai import cli

    monkeypatch.setenv("OWNYOURAI_HOME", str(tmp_path / "oya-home"))
    cli.main(["init", "--no-passphrase"])

    rc = cli.main(["audit", "summary"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "No audit entries" in out


# ---------------------------------------------------------------------------
# oya audit anchor subcommand tests
# ---------------------------------------------------------------------------


def test_audit_anchor_succeeds(tmp_path, keys, monkeypatch, capsys):
    """anchor writes timestamps.jsonl and prints token info."""
    import json as _json

    from ownyourai import cli, config

    monkeypatch.setenv("OWNYOURAI_HOME", str(tmp_path / "oya-home"))
    cli.main(["init", "--no-passphrase"])

    log = config.audit_log_path()
    append_entry(log, message="hello", operator_type="HUMAN", private_key_pem=keys["human_priv"])

    fake_token = b"\x30\x10" + b"\x00" * 14
    mock_resp = MagicMock()
    mock_resp.read.return_value = fake_token
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        rc = cli.main(["audit", "anchor"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "anchored_at" in out

    ts_store = config.home_dir() / "timestamps.jsonl"
    assert ts_store.exists()
    saved = _json.loads(ts_store.read_text().strip())
    assert saved["token_hex"] == fake_token.hex()


def test_audit_anchor_fails_without_log(tmp_path, monkeypatch, capsys):
    """anchor returns rc=1 when audit log is missing."""
    from ownyourai import cli

    monkeypatch.setenv("OWNYOURAI_HOME", str(tmp_path / "oya-home"))
    cli.main(["init", "--no-passphrase"])

    rc = cli.main(["audit", "anchor"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "empty or does not exist" in err
