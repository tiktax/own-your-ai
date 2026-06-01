"""End-to-end CLI tests via the `main()` entry point."""

import json

import pytest

from ownyourai import cli


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("OWNYOURAI_HOME", str(tmp_path / "oya-home"))
    return tmp_path / "oya-home"


def test_init_creates_keys(home):
    assert cli.main(["init", "--no-passphrase"]) == 0
    assert (home / "keys" / "human_private_key.pem").exists()
    assert (home / "keys" / "human_public_key.pem").exists()
    assert (home / "keys" / "ai_private_key.pem").exists()
    assert (home / "keys" / "ai_public_key.pem").exists()
    assert (home / "config.toml").exists()


def test_init_refuses_overwrite_without_force(home, capsys):
    cli.main(["init", "--no-passphrase"])
    rc = cli.main(["init", "--no-passphrase"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "already exists" in captured.err


def test_init_force_overwrites(home):
    cli.main(["init", "--no-passphrase"])
    assert cli.main(["init", "--force", "--no-passphrase"]) == 0


def test_sign_verify_roundtrip(home):
    cli.main(["init", "--no-passphrase"])
    assert cli.main(["sign", "-m", "test message", "--as", "human"]) == 0
    assert cli.main(["sign", "-m", "ai message", "--as", "ai"]) == 0
    assert cli.main(["verify"]) == 0


def test_audit_list(home, capsys):
    cli.main(["init", "--no-passphrase"])
    cli.main(["sign", "-m", "first", "--as", "human"])
    cli.main(["sign", "-m", "second", "--as", "ai"])
    capsys.readouterr()  # clear

    assert cli.main(["audit", "list"]) == 0
    out = capsys.readouterr().out
    assert "first" in out
    assert "second" in out
    assert "HUMAN" in out
    assert "AI" in out


def test_audit_show_specific_line(home, capsys):
    cli.main(["init", "--no-passphrase"])
    cli.main(["sign", "-m", "hello", "--as", "human"])
    capsys.readouterr()

    assert cli.main(["audit", "show", "1"]) == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["message"] == "hello"
    assert payload["operator_type"] == "HUMAN"


def test_audit_show_out_of_range(home):
    cli.main(["init", "--no-passphrase"])
    cli.main(["sign", "-m", "hello", "--as", "human"])
    assert cli.main(["audit", "show", "99"]) == 1


def test_export_outputs_valid_json(home, capsys):
    cli.main(["init", "--no-passphrase"])
    cli.main(["sign", "-m", "exported", "--as", "human"])
    capsys.readouterr()

    assert cli.main(["export"]) == 0
    bundle = json.loads(capsys.readouterr().out)
    assert bundle["schema"] == "own-your-ai.export/v1"
    assert bundle["entry_count"] == 1
    assert bundle["entries"][0]["message"] == "exported"


def test_sign_fails_without_init(home, capsys):
    rc = cli.main(["sign", "-m", "x", "--as", "human"])
    assert rc == 1
    assert "private key not found" in capsys.readouterr().err


def test_passphrase_encrypted_roundtrip(home, monkeypatch, capsys):
    monkeypatch.setenv("OWNYOURAI_PASSPHRASE", "testpass")
    assert cli.main(["init"]) == 0
    assert cli.main(["sign", "-m", "encrypted key test", "--as", "human"]) == 0
    assert cli.main(["verify"]) == 0


def test_verify_detects_tampering(home, tmp_path):
    cli.main(["init", "--no-passphrase"])
    cli.main(["sign", "-m", "original", "--as", "human"])

    log = home / "audit.jsonl"
    line = log.read_text().strip()
    entry = json.loads(line)
    entry["message"] = "tampered"
    log.write_text(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")

    assert cli.main(["verify"]) == 2


def test_verify_shows_anchor_when_present(home, capsys):
    """verify prints timestamp anchor info when timestamps.jsonl exists."""
    cli.main(["init", "--no-passphrase"])
    cli.main(["sign", "-m", "hello", "--as", "human"])

    # Write a fake anchor record
    anchor_record = json.dumps({
        "anchored_at": "2026-05-28T15:42:11.123456+00:00",
        "log_hash": "abc123",
        "log_entry_count": 1,
        "tsa_url": "https://freetsa.org/tsr",
        "token_hex": "deadbeef",
    })
    (home / "timestamps.jsonl").write_text(anchor_record + "\n")

    rc = cli.main(["verify"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Timestamp anchor" in out
    assert "2026-05-28T15:42:11Z" in out
    assert "freetsa.org" in out
    assert "1 log entries" in out


def test_verify_shows_anchor_hint_when_absent(home, capsys):
    """verify prints a hint to run anchor when no timestamps.jsonl exists."""
    cli.main(["init", "--no-passphrase"])
    cli.main(["sign", "-m", "hello", "--as", "human"])

    rc = cli.main(["verify"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "oya audit anchor" in out


def test_verify_shows_token_count_when_multiple(home, capsys):
    """verify shows [N tokens] when more than one anchor exists."""
    cli.main(["init", "--no-passphrase"])
    cli.main(["sign", "-m", "hello", "--as", "human"])

    record = json.dumps({
        "anchored_at": "2026-05-28T10:00:00+00:00",
        "log_hash": "aaa",
        "log_entry_count": 1,
        "tsa_url": "https://freetsa.org/tsr",
        "token_hex": "aa",
    })
    ts_store = home / "timestamps.jsonl"
    ts_store.write_text(record + "\n" + record + "\n")  # 2 tokens

    rc = cli.main(["verify"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "2 tokens" in out
