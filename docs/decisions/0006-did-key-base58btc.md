# ADR-0006: did:key encoding — base58btc (Phase 2)

**Status**: Accepted
**Date**: 2026-05-27
**Supersedes**: Phase 1 stub in ADR-0002

## Context

Phase 1 used base64url encoding (`did:key:u...`) for simplicity. This is non-standard:
W3C DID Core and the did:key method spec mandate base58btc multibase encoding (`did:key:z...`).
Interoperability with other DID tools, wallets, and verifiable credential libraries requires
spec-compliant encoding.

## Decision

Replace `base64.urlsafe_b64encode` with `base58.b58encode` in `identity/did.py`.
- Multibase prefix changes from `u` to `z` (base58btc)
- Multicodec prefix for P-256 remains `0x1200` (varint: `0x80 0x24`)
- Add `base58>=2.1` to project dependencies

## Breaking Change

Existing `did:key:u...` identifiers generated in Phase 1 are invalidated.
Users who ran `oya init` in Phase 1 should re-run `oya init --force` to regenerate keys
with spec-compliant DIDs. The audit log itself is unaffected; only the displayed DID changes.

## Alternatives Considered

| Option | Why not chosen |
|---|---|
| Keep base64url | Non-standard; breaks interoperability with DID tools and VC libraries |
| Implement base58btc manually | Unnecessary: `base58` package is stable, minimal, no transitive deps |
| did:key via `did-key-py` library | Over-engineered for Phase 2; `base58` + our existing multicodec prefix is sufficient |

## Consequences

- `derive_did_key()` now returns `did:key:z{base58btc}` — W3C DID Core spec compliant
- Phase 3+ DID libraries (did:web, did:peer) will interoperate correctly
- `base58>=2.1` added to production dependencies (pure Python, ~6 KB)
