"""Tests for ownyourai.llm.ollama and ownyourai.commands.chat."""

import json
from unittest.mock import MagicMock, patch

import pytest

from ownyourai import cli
from ownyourai.llm.ollama import OllamaError, chat, list_models

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_urlopen(response_data: dict):
    """Return a context-manager mock that yields a readable HTTP response."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


_CHAT_OK = {"message": {"role": "assistant", "content": "4"}, "done": True}
_TAGS_OK = {"models": [{"name": "gemma3"}, {"name": "llama3"}]}


# ---------------------------------------------------------------------------
# llm/ollama.py unit tests
# ---------------------------------------------------------------------------


def test_ollama_chat_returns_response():
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(_CHAT_OK)):
        result = chat([{"role": "user", "content": "2+2"}], model="gemma3")
    assert result == "4"


def test_ollama_chat_connection_error():
    import urllib.error

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
        with pytest.raises(OllamaError, match="Cannot connect"):
            chat([], model="gemma3")


def test_ollama_list_models():
    with patch("urllib.request.urlopen", return_value=_mock_urlopen(_TAGS_OK)):
        models = list_models()
    assert "gemma3" in models
    assert "llama3" in models


# ---------------------------------------------------------------------------
# commands/chat.py integration tests (ollama mocked)
# ---------------------------------------------------------------------------


@pytest.fixture
def chat_home(tmp_path, monkeypatch):
    monkeypatch.setenv("OWNYOURAI_HOME", str(tmp_path / "oya-home"))
    monkeypatch.setenv("OWNYOURAI_PASSPHRASE", "")
    cli.main(["init", "--no-passphrase"])
    return tmp_path / "oya-home"


def test_chat_run_exits_on_q(chat_home, capsys):
    with (
        patch("urllib.request.urlopen", return_value=_mock_urlopen(_TAGS_OK)),
        patch("builtins.input", side_effect=["q"]),
    ):
        rc = cli.main(["chat", "--no-passphrase", "--log-level", "none"])
    assert rc == 0
    assert "Session ended" in capsys.readouterr().out


def test_chat_run_exits_on_eof(chat_home, capsys):
    with (
        patch("urllib.request.urlopen", return_value=_mock_urlopen(_TAGS_OK)),
        patch("builtins.input", side_effect=EOFError),
    ):
        rc = cli.main(["chat", "--no-passphrase", "--log-level", "none"])
    assert rc == 0


def test_log_level_none(chat_home):
    """--log-level none: no audit entries created."""
    from ownyourai import config
    from ownyourai.audit.log import read_entries

    with (
        patch(
            "urllib.request.urlopen",
            side_effect=[_mock_urlopen(_TAGS_OK), _mock_urlopen(_CHAT_OK)],
        ),
        patch("builtins.input", side_effect=["hello", "q"]),
    ):
        cli.main(["chat", "--no-passphrase", "--log-level", "none"])

    entries = read_entries(config.audit_log_path())
    assert len(entries) == 0


def test_log_level_summary(chat_home):
    """--log-level summary: 1 entry for the whole session."""
    from ownyourai import config
    from ownyourai.audit.log import read_entries

    with (
        patch(
            "urllib.request.urlopen",
            side_effect=[_mock_urlopen(_TAGS_OK), _mock_urlopen(_CHAT_OK)],
        ),
        patch("builtins.input", side_effect=["hello", "q"]),
    ):
        cli.main(["chat", "--no-passphrase", "--log-level", "summary"])

    entries = read_entries(config.audit_log_path())
    assert len(entries) == 1
    assert entries[0]["action"] == "chat_session"
    assert entries[0]["operator_type"] == "HUMAN"
    assert "gemma3" in entries[0]["message"]


def test_log_level_full(chat_home):
    """--log-level full: 2 entries per turn (prompt + response)."""
    from ownyourai import config
    from ownyourai.audit.log import read_entries

    with (
        patch(
            "urllib.request.urlopen",
            side_effect=[
                _mock_urlopen(_TAGS_OK),
                _mock_urlopen(_CHAT_OK),
                _mock_urlopen(_CHAT_OK),
            ],
        ),
        patch("builtins.input", side_effect=["hello", "world", "q"]),
    ):
        cli.main(["chat", "--no-passphrase", "--log-level", "full"])

    entries = read_entries(config.audit_log_path())
    assert len(entries) == 4  # 2 turns × 2 entries
    actions = [e["action"] for e in entries]
    assert actions == ["chat_prompt", "chat_response", "chat_prompt", "chat_response"]


def test_chat_empty_response_skips_logging(chat_home, capsys):
    """Empty response from ollama: no log entry, warning printed."""
    from ownyourai import config
    from ownyourai.audit.log import read_entries

    empty_resp = {"message": {"role": "assistant", "content": ""}, "done": True}
    with (
        patch(
            "urllib.request.urlopen",
            side_effect=[_mock_urlopen(_TAGS_OK), _mock_urlopen(empty_resp)],
        ),
        patch("builtins.input", side_effect=["hello", "q"]),
    ):
        cli.main(["chat", "--no-passphrase", "--log-level", "full"])

    entries = read_entries(config.audit_log_path())
    assert len(entries) == 1  # only the prompt entry (no response entry)
    assert "empty response" in capsys.readouterr().err


def test_chat_fails_without_init(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("OWNYOURAI_HOME", str(tmp_path / "empty"))
    rc = cli.main(["chat", "--no-passphrase"])
    assert rc == 1
    assert "oya init" in capsys.readouterr().err
