# ADR-0003: Key storage uses filesystem PEM in Phase 1

- **Status**: Accepted (with known gap for passphrase encryption)
- **Date**: 2026-05-26

## Context

Where do private keys live? Options considered:

1. **Plain PEM file** with strict permissions (mode 600)
2. **Passphrase-encrypted PEM** (PKCS#8 with PBKDF2/scrypt)
3. **macOS Keychain** via `security` CLI or PyObjC bindings
4. **Secure Enclave** (P-256 keys, hardware-bound, non-exportable)

## Decision

Phase 1 ships **option 1: plain PEM at `~/.ownyourai/keys/`, mode 600**. The smoke test must work without prompting for a passphrase.

Option 2 (passphrase) is scheduled as a **Phase 1.x patch** before any non-test data lives in audit logs. The `generate_keypair()` function already takes a `password` parameter on the load side; the patch is a UX layer.

Options 3 (Keychain) and 4 (Secure Enclave) are deferred to Phase 2.

## Consequences

**Positive**:
- The simplest thing that works; no platform-specific dependencies
- Easy to test, easy to back up, easy to migrate
- The user can grep / cat / inspect their own keys

**Negative**:
- A reader of `~/.ownyourai/keys/*_private_key.pem` can forge any future audit entry
- File-permission-only protection assumes the OS user model is sound (T2 in [threat-model.md](../threat-model.md))
- Backups copy the keys verbatim — backup compromise = key compromise (T4)

## When to revisit

**Phase 1.x** must add passphrase encryption before the project is recommended for general use.

**Phase 2** evaluates Keychain (broad protection, locks to macOS) vs Secure Enclave (hardware protection, but P-256 only and key export is restricted) and chooses one as the default.
