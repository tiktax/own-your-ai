"""End-to-end CLI tests via the `main()` entry point."""

import json

import pytest

from ownyourai import cli


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("OWNYOURAI_HOME", str(tmp_path / "oya-home"))
    return tmp_path / "oya-home"


def test_init_creates_keys(home):
    assert cli.main(["init"]) == 0
    assert (home / "keys" / "human_private_key.pem").exists()
    assert (home / "keys" / "human_public_key.pem").exists()
    assert (home / "keys" / "ai_private_key.pem").exists()
    assert (home / "keys" / "ai_public_key.pem").exists()
    assert (home / "config.toml").exists()


def test_init_refuses_overwrite_without_force(home, capsys):
    cli.main(["init"])
    rc = cli.main(["init"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "already exists" in captured.err


def test_init_force_overwrites(home):
    cli.main(["init"])
    assert cli.main(["init", "--force"]) == 0


def test_sign_verify_roundtrip(home):
    cli.main(["init"])
    assert cli.main(["sign", "-m", "test message", "--as", "human"]) == 0
    assert cli.main(["sign", "-m", "ai message", "--as", "ai"]) == 0
    assert cli.main(["verify"]) == 0


def test_audit_list(home, capsys):
    cli.main(["init"])
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
    cli.main(["init"])
    cli.main(["sign", "-m", "hello", "--as", "human"])
    capsys.readouterr()

    assert cli.main(["audit", "show", "1"]) == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["message"] == "hello"
    assert payload["operator_type"] == "HUMAN"


def test_audit_show_out_of_range(home):
    cli.main(["init"])
    cli.main(["sign", "-m", "hello", "--as", "human"])
    assert cli.main(["audit", "show", "99"]) == 1


def test_export_outputs_valid_json(home, capsys):
    cli.main(["init"])
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


def test_verify_detects_tampering(home, tmp_path):
    cli.main(["init"])
    cli.main(["sign", "-m", "original", "--as", "human"])

    log = home / "audit.jsonl"
    line = log.read_text().strip()
    entry = json.loads(line)
    entry["message"] = "tampered"
    log.write_text(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")

    assert cli.main(["verify"]) == 2
