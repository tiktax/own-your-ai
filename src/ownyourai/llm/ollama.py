"""
llm/ollama.py — thin HTTP wrapper for ollama's REST API.

Uses stdlib urllib.request only; no additional dependencies.
Supports /api/chat (chat completion) and /api/tags (model listing).
"""

import json
import socket
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse


def _assert_local_url(url: str) -> None:
    """Warn if the ollama URL resolves to a non-loopback address.

    This is a data-sovereignty safeguard: oya is designed for local-only LLMs.
    A non-localhost URL could route conversation history off-device.

    Uses getaddrinfo (not gethostbyname) so that both IPv4 (127.x) and
    IPv6 (::1) loopback addresses are recognised correctly.
    """
    host = urlparse(url).hostname or "localhost"
    try:
        results = socket.getaddrinfo(host, None)
        addrs = [r[4][0] for r in results]
    except socket.gaierror:
        return  # cannot resolve; let the connection attempt fail naturally
    non_local = [a for a in addrs if not (a.startswith("127.") or a == "::1")]
    if non_local:
        print(
            f"warning: --ollama-url resolves to {non_local[0]}"
            " — conversation data may leave device",
            file=sys.stderr,
        )


class OllamaError(Exception):
    """Raised when ollama is unreachable or returns an unexpected response."""


def chat(
    messages: list[dict],
    model: str,
    base_url: str = "http://localhost:11434",
    timeout: int = 120,
) -> str:
    """POST /api/chat with stream=false. Returns the assistant's response text."""
    _assert_local_url(base_url)
    payload = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
        return result["message"]["content"]
    except urllib.error.URLError as exc:
        raise OllamaError(f"Cannot connect to ollama at {base_url}: {exc}") from exc
    except (KeyError, json.JSONDecodeError) as exc:
        raise OllamaError(f"Unexpected response from ollama: {exc}") from exc


def list_models(base_url: str = "http://localhost:11434") -> list[str]:
    """GET /api/tags. Returns list of available model names."""
    _assert_local_url(base_url)
    req = urllib.request.Request(f"{base_url}/api/tags")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        return [m["name"] for m in result.get("models", [])]
    except urllib.error.URLError as exc:
        raise OllamaError(f"Cannot connect to ollama at {base_url}: {exc}") from exc
    except (KeyError, json.JSONDecodeError) as exc:
        raise OllamaError(f"Unexpected response from ollama: {exc}") from exc
