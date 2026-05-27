# ADR-0005: Passphrase Encryption for Private Keys

**Status**: Accepted
**Date**: 2026-05-27

## Context

Phase 1 stored private key PEMs on the filesystem with `chmod 0600` but without encryption. ADR-0003 acknowledged this as a known Phase 1 gap. A co-resident user, backup leak, or accidental git commit could expose the plaintext key material.

## Decision

Encrypt private key PEMs at rest using `cryptography`'s `BestAvailableEncryption` (currently AES-256-CBC with PBKDF2-HMAC-SHA256).

`oya init` prompts for a passphrase at key generation time:
- If `OWNYOURAI_PASSPHRASE` env var is set, use it (CI / automated testing).
- `--no-passphrase` skips encryption (explicitly insecure; for testing only).
- Empty passphrase at the prompt is accepted with a warning (user choice).

`oya sign` auto-detects whether the stored key is encrypted:
- Tries `password=None` first; on `TypeError` or `ValueError`, prompts or reads `OWNYOURAI_PASSPHRASE`.

## Alternatives Considered

| Option | Why not chosen |
|---|---|
| macOS Keychain | Phase 2 scope; requires platform-specific dependency |
| Secure Enclave | Phase 4+; hardware dependency |
| No encryption (status quo) | Known security gap — unacceptable beyond Phase 1 |

## Consequences

- `oya sign` now requires a passphrase for encrypted keys (interactive or via env var).
- `--no-passphrase` flag exists, so encryption is not enforced. This is intentional: enforcement will come in Phase 2 with Keychain integration.
- Existing Phase 1 keys (unencrypted) continue to work; `oya sign` detects and loads them without prompting.
