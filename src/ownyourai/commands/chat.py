"""`oya chat` — interactive REPL backed by a local ollama LLM."""

import sys

from .. import config
from ..audit.log import append_entry
from ..crypto.passphrase import resolve_passphrase
from ..llm.ollama import OllamaError, list_models
from ..llm.ollama import chat as ollama_chat

DEFAULT_OLLAMA_URL = "http://localhost:11434"


def run(args) -> int:
    model: str = args.model
    base_url: str = args.ollama_url
    log_level: str = args.log_level
    timeout: int = args.timeout
    max_history: int = args.max_history

    human_priv_path = config.private_key_path("human")
    ai_priv_path = config.private_key_path("ai")
    if not human_priv_path.exists() or not ai_priv_path.exists():
        print("error: keys not found. Run `oya init` first.", file=sys.stderr)
        return 1

    human_priv = human_priv_path.read_bytes()
    ai_priv = ai_priv_path.read_bytes()
    passphrase = resolve_passphrase(human_priv, no_passphrase=getattr(args, "no_passphrase", False))

    try:
        available = list_models(base_url)
    except OllamaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Auto-detect model if not specified
    if model is None:
        if not available:
            print(
                "error: no models found in ollama. Run `ollama pull <model>` first.",
                file=sys.stderr,
            )
            return 1
        model = available[0]
        print(f"Auto-selected model: {model}")

    print(f"Connected to ollama (model: {model})")
    if available and not any(m == model or m.startswith(model + ":") for m in available):
        print(
            f"warning: '{model}' not found. Available: {', '.join(available[:5])}",
            file=sys.stderr,
        )
    print("Type 'q' or 'exit' to quit. Conversation is logged to audit.jsonl.\n")

    history: list[dict] = []
    turns = 0
    first_prompt = ""
    log_path = config.audit_log_path()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ("q", "exit", "quit"):
            break
        if not user_input:
            continue

        if not first_prompt:
            first_prompt = user_input

        if log_level == "full":
            append_entry(
                log_path,
                message=user_input,
                operator_type="HUMAN",
                private_key_pem=human_priv,
                action="chat_prompt",
                passphrase=passphrase,
            )

        history.append({"role": "user", "content": user_input})
        # Trim context window to avoid exceeding model limits.
        # After slicing, drop any leading assistant turns so the context always
        # starts with a user message (required by most LLM APIs).
        trimmed = history[-(max_history * 2):] if max_history > 0 else history
        while trimmed and trimmed[0]["role"] != "user":
            trimmed = trimmed[1:]
        try:
            response = ollama_chat(trimmed, model=model, base_url=base_url, timeout=timeout)
        except OllamaError as exc:
            print(f"error: {exc}", file=sys.stderr)
            history.pop()
            continue

        if not response:
            print("warning: empty response from model", file=sys.stderr)
            history.pop()
            continue

        print(f"Assistant: {response}\n")
        history.append({"role": "assistant", "content": response})
        turns += 1

        if log_level == "full":
            append_entry(
                log_path,
                message=f"[{model}] {response}",
                operator_type="AI",
                private_key_pem=ai_priv,
                action="chat_response",
                passphrase=passphrase,
            )

    if turns > 0 and log_level == "summary":
        summary = f"[{model}] {turns} turns — {first_prompt[:60]}"
        if len(first_prompt) > 60:
            summary += "..."
        append_entry(
            log_path,
            message=summary,
            operator_type="HUMAN",
            private_key_pem=human_priv,
            action="chat_session",
            passphrase=passphrase,
        )

    logged = (
        turns * 2 if log_level == "full" else (1 if turns > 0 and log_level == "summary" else 0)
    )
    entry_word = "entry" if logged == 1 else "entries"
    print(f"Session ended. {turns} turns, {logged} log {entry_word}.")
    return 0


def register(subparsers) -> None:
    p = subparsers.add_parser("chat", help="interactive chat with a local LLM via ollama")
    p.add_argument(
        "--model",
        default=None,
        help="ollama model name (default: auto-detect first available)",
    )
    p.add_argument(
        "--ollama-url",
        dest="ollama_url",
        default=DEFAULT_OLLAMA_URL,
        help=f"ollama base URL (default: {DEFAULT_OLLAMA_URL})",
    )
    p.add_argument(
        "--no-passphrase",
        action="store_true",
        dest="no_passphrase",
        help="skip passphrase prompt (for unencrypted keys)",
    )
    p.add_argument(
        "--log-level",
        dest="log_level",
        choices=("none", "summary", "full"),
        default="summary",
        help="audit log granularity: none | summary (default) | full",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="ollama response timeout in seconds (default: 120)",
    )
    p.add_argument(
        "--max-history",
        dest="max_history",
        type=int,
        default=50,
        help="max conversation turns to keep in context window (default: 50, 0=unlimited)",
    )
    p.set_defaults(func=run)
