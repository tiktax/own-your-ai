"""
llm/ollama.py — thin HTTP wrapper for ollama's REST API.

Uses stdlib urllib.request only; no additional dependencies.
Supports /api/chat (chat completion) and /api/tags (model listing).
"""

import json
import urllib.error
import urllib.request


class OllamaError(Exception):
    """Raised when ollama is unreachable or returns an unexpected response."""


def chat(
    messages: list[dict],
    model: str,
    base_url: str = "http://localhost:11434",
) -> str:
    """POST /api/chat with stream=false. Returns the assistant's response text."""
    payload = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        return result["message"]["content"]
    except urllib.error.URLError as exc:
        raise OllamaError(f"Cannot connect to ollama at {base_url}: {exc}") from exc
    except (KeyError, json.JSONDecodeError) as exc:
        raise OllamaError(f"Unexpected response from ollama: {exc}") from exc


def list_models(base_url: str = "http://localhost:11434") -> list[str]:
    """GET /api/tags. Returns list of available model names."""
    req = urllib.request.Request(f"{base_url}/api/tags")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        return [m["name"] for m in result.get("models", [])]
    except urllib.error.URLError as exc:
        raise OllamaError(f"Cannot connect to ollama at {base_url}: {exc}") from exc
    except (KeyError, json.JSONDecodeError) as exc:
        raise OllamaError(f"Unexpected response from ollama: {exc}") from exc
