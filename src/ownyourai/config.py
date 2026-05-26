"""config.py — Path resolution for ~/.ownyourai/."""

import os
from pathlib import Path


def home_dir() -> Path:
    """Base directory for own-your-ai user data. Override with OWNYOURAI_HOME env var."""
    override = os.environ.get("OWNYOURAI_HOME")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".ownyourai"


def keys_dir() -> Path:
    return home_dir() / "keys"


def audit_log_path() -> Path:
    return home_dir() / "audit.jsonl"


def config_path() -> Path:
    return home_dir() / "config.toml"


def private_key_path(role: str) -> Path:
    if role not in ("human", "ai"):
        raise ValueError(f"role must be 'human' or 'ai', got {role!r}")
    return keys_dir() / f"{role}_private_key.pem"


def public_key_path(role: str) -> Path:
    if role not in ("human", "ai"):
        raise ValueError(f"role must be 'human' or 'ai', got {role!r}")
    return keys_dir() / f"{role}_public_key.pem"
