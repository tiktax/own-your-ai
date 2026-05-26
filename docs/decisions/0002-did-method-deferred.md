# ADR-0002: did:key only in Phase 1; did:web and others deferred

- **Status**: Accepted
- **Date**: 2026-05-26

## Context

DID (Decentralized Identifier) methods range from completely self-contained (`did:key` — derive from a public key, no external state) to network-dependent (`did:web`, `did:ion`, `did:peer`).

Phase 1's goal is a working foundation that doesn't pull external dependencies. The user has no domain, no public registry, no peer to negotiate with.

## Decision

Phase 1 implements only **`did:key`** and even that as a stub: we use base64url multibase (`u` prefix) instead of the spec-compliant base58btc (`z` prefix). The function `derive_did_key()` in `src/ownyourai/identity/did.py` exists to let `oya init` print *something* DID-shaped, and to let future code call into a stable interface.

`did:web`, `did:peer`, `did:ion`, `did:ebsi`, etc. are deferred to Phase 2.

## Consequences

**Positive**:
- Zero external dependencies for identity in Phase 1
- The interface (`derive_did_key(pub_pem) -> str`) is stable; Phase 2 swaps the implementation
- Users see their DID immediately on `oya init`

**Negative**:
- The Phase 1 DIDs are **not interoperable** with the wider DID ecosystem (base64url vs base58btc)
- Any third-party VC verifier that tries to resolve a Phase 1 DID will fail

## When to revisit

**Phase 2 must** replace the stub with a spec-compliant `did:key` (base58btc, RFC 4648) before any cross-tool interop is attempted. This ADR will be superseded then.
