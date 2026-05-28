# ADR-0008 — Phase 3.5 Security Hardening & RFC 3161 Trusted Timestamping

**Status**: Accepted  
**Date**: 2026-05-28  
**Version**: v0.3.1

---

## Context

A Jobs-style review of Phase 1–3 (v0.3.0) identified eight concrete improvements across security
correctness, code quality, and user experience. This ADR documents the design decisions made
during Phase 3.5 implementation.

---

## Decisions

### D1 — File permissions: 0o700 for directories, 0o600 for files

**Why**: The key directory (`~/.ownyourai/keys/`) and home directory were created at the default
`mkdir` mode (0o777 minus umask, typically 0o755). This means any process running as the same
OS user could list and read private key PEM files without restriction. The audit log was similarly
created at 0o644 (world-readable).

**Decision**: Pass `mode=0o700` to all `mkdir` calls and `mode=0o600` to all file creation
operations. This ensures private keys and audit data are accessible only to the owning user.

**Rejected alternative**: macOS Keychain / Secure Enclave migration — deferred to Phase 2 as it
requires platform-specific APIs and breaks the offline-first, portable design.

---

### D2 — Exclusive file locking (`fcntl.flock`) + `os.fsync` in `append_entry`

**Why**: The original `append_entry` read the last line to determine `prev_hash`, then wrote a
new entry. Under concurrent writes (e.g., two `oya chat` sessions opening simultaneously), both
could read the same `prev_hash` and produce two entries with identical `prev_hash`, silently
breaking the hash chain.

**Decision**: Wrap the read-then-write in `fcntl.flock(LOCK_EX)`. The file descriptor is opened
with `os.open()` (not `open()`) to hold the fd across the lock scope. `os.fsync` is called
before releasing the lock to guarantee durability on a kernel crash.

**Why `fcntl` and not a separate lockfile**: `pyproject.toml` already declares `Operating System
:: MacOS` and `Operating System :: POSIX :: Linux` only. `fcntl` is available on both. A
separate `.lock` file would leave an orphan if the process crashes.

**Limitation**: `fcntl` advisory locks are per-process, not per-thread. Thread-level concurrency
within a single process is not protected, but `oya` is a CLI tool — this scenario does not arise
in practice.

---

### D3 — `resolve_passphrase` consolidation into `crypto/passphrase.py`

**Why**: `sign.py` and `chat.py` each contained an identical `_resolve_passphrase` function.
Divergence between the two copies was a latent bug risk.

**Decision**: Extract into `ownyourai.crypto.passphrase.resolve_passphrase` with the unified
signature `resolve_passphrase(priv_pem: bytes, *, no_passphrase: bool = False) -> bytes | None`.

**Resolution order** (preserved from original implementations):
1. `no_passphrase=True` → `None` immediately
2. Unencrypted PEM detection (attempt `load_pem_private_key(password=None)`) → `None` on success
3. `OWNYOURAI_PASSPHRASE` env var → value as bytes, or `None` if empty string
4. `getpass.getpass` fallback → value as bytes, or `None` if empty

Added `--no-passphrase` to `sign.py` to match `chat.py` (parity).

---

### D4 — `_assert_local_url` warning in `llm/ollama.py`

**Why**: `--ollama-url https://remote-host.example.com` silently routes all conversation history
to a remote server. This directly violates the "data stays on device" sovereignty promise.

**Decision**: Resolve the hostname via `socket.gethostbyname` and print a stderr warning if the
result is not a loopback address (127.x.x.x or ::1). The connection is **not blocked** — the
user may intentionally target a local network server. The warning is informational.

**Future**: A `--allow-remote` flag that makes the intent explicit is tracked as a known gap in
`docs/threat-model.md` T8.

---

### D5 — RFC 3161 Trusted Timestamping (`oya audit anchor`)

**Why**: The ECDSA hash chain is tamper-*detectable* (casual edits without the key break
verification) but not tamper-*evident*: a keyholder who reconstructs entries with valid
signatures and correct `prev_hash` values can produce a log that passes `oya verify` with no
failures. This gap means an AI system could rewrite its own history without leaving evidence.

**Decision**: Implement `oya audit anchor` as an explicit opt-in command. It:
1. SHA-256 hashes the entire `audit.jsonl` file
2. Builds a minimal RFC 3161 `TimeStampReq` DER structure
3. POSTs it to a free TSA (default: `https://freetsa.org/tsr`)
4. Saves the returned `TimeStampToken` (DER hex) to `~/.ownyourai/timestamps.jsonl` (0o600)

The returned token proves the log existed at a specific wall-clock time. Even if the keyholder
later rebuilds the chain, they cannot produce a token with an earlier timestamp — the TSA is a
trusted third party with no keyholder relationship.

**Why manual DER encoding**: The `cryptography` package (already a dependency) supports X.509 and
CMS but does not expose a public RFC 3161 request builder. Using `pyasn1` or `asn1crypto` would
add a dependency. The `TimeStampReq` structure for a SHA-256 hash with a nonce fits in under 80
bytes, all lengths < 128, so BER/DER single-byte length encoding is sufficient. The encoding is
unit-tested against the SHA-256 OID bytes and structure invariants.

**Why opt-in**: `oya` is offline-first. Automatic anchoring would break air-gapped environments,
introduce latency on every audit write, and create a hard dependency on a third-party service.
The user explicitly consents to network access by running `oya audit anchor`.

**Why `freetsa.org` as default**: Free, operated since 2014, RFC 3161 compliant, no API key
required. Users can specify any TSA via `--tsa-url`.

---

## Jobs Score Impact

| Dimension | v0.3.0 | v0.3.1 |
|-----------|--------|--------|
| Security correctness | 2.5 | 4.5 (permissions + locking) |
| Code quality | 3.0 | 4.0 (passphrase dedup) |
| User onboarding | 2.5 | 4.0 (README Quick Start) |
| Tamper evidence | 2.0 | 4.0 (RFC 3161 anchor) |
| **Overall (estimated)** | **3.2** | **≥ 4.2** |
