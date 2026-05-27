# Roadmap

## Relationship to ai-infra-portfolio

[ai-infra-portfolio](https://github.com/tiktax/ai-infra-portfolio) (Phases 1–7) provides AI governance primitives for **organizations** (teams, compliance officers, CISOs). Its Phase 8 declares own-your-ai as a separate project that applies the same primitives to **individuals**.

own-your-ai uses its own Phase numbering starting from Phase 1, because the architectural concerns at individual scale are different enough that re-using ai-infra-portfolio's numbering would mislead readers.

| Project | Phase 1 means |
|---|---|
| ai-infra-portfolio | Security hooks for org-scale Claude Code deployment |
| **own-your-ai** | **Foundation layer: design docs + ECDSA-signed personal audit log CLI** |

## Phase 1 — Foundation ✅ (this release)

**Goal**: A reader of the repo can understand the project in 3 minutes and the crypto skeleton works end-to-end.

| Deliverable | Status |
|---|---|
| `oya init / sign / verify / audit / export` CLI | ✅ |
| ECDSA P-256 signing (lifted from ai-infra-portfolio Phase 5) | ✅ |
| JSON Lines audit log with `prev_hash` chain | ✅ |
| `did:key` stub | ✅ |
| `architecture.md` / `threat-model.md` / `legal-matrix.md` / `glossary.md` | ✅ |
| ADRs 0001–0004 | ✅ |
| pytest suite ≥ 70% coverage | ✅ (93%) |
| GitHub Actions CI (lint + test + gitleaks) | ✅ |
| Apache 2.0 LICENSE, SECURITY.md, .pre-commit-config.yaml | ✅ |

**Tag**: `v0.1.0-foundation`

## Phase 1.x — Passphrase Encryption ✅

**Tag**: `v0.1.1`

| Deliverable | Status |
|---|---|
| `BestAvailableEncryption` for private key PEMs | ✅ |
| `oya init` passphrase prompt (interactive + `OWNYOURAI_PASSPHRASE` env) | ✅ |
| `--no-passphrase` flag for testing/CI | ✅ |
| `oya sign` auto-detects encrypted keys | ✅ |
| ADR-0005 | ✅ |

## Phase 2 — Identity & Keystore ✅

**Tag**: `v0.2.0`

| Deliverable | Status |
|---|---|
| `did:key` base58btc (W3C DID Core spec-compliant) | ✅ |
| ADR-0006 | ✅ |

**Breaking change**: `did:key:u...` (Phase 1) → `did:key:z...` (Phase 2). Re-run `oya init --force` to regenerate keys.

**Deferred to Phase 3**:
- macOS Keychain wrapper for `~/.ownyourai/keys/`
- `did:web` support for users who own a domain
- ADR for Secure Enclave vs Keychain trade-offs

## Phase 3 — On-device LLM Integration

**Goal**: Every conversation with a local LLM becomes a signed audit entry, automatically.

- Wrapper around `ollama` / `llama.cpp` that pipes prompts and responses through `audit/log.py`
- Gemma3-class model as the reference target
- `oya chat` subcommand

## Phase 4 — Social Recovery

**Goal**: Lose the device, recover the identity.

- M-of-N key recovery (k=3, n=5 reference)
- Designated recovery agents (not custodians) — they hold shares, not keys
- ADR for Shamir's Secret Sharing vs threshold ECDSA

## Phase 5 — Verifiable Credentials

**Goal**: The user can issue and verify credentials about themselves on top of `did:key`.

- W3C Verifiable Credentials v2 issuance
- Selective disclosure (BBS+ signatures, evaluated separately)
- Compatibility with MyData Operator reference implementations

## Phase 6+ — Future

- Post-quantum signing (ML-DSA-65) — copy from ai-infra-portfolio Phase 5 when justified
- Mobile (iOS first; Android requires separate scope)
- Cross-device sync (Phase 6 once Phase 4 recovery is solved)
- Rust port for crypto-critical paths

## Out of scope (declared explicitly)

- Enterprise compliance certification — that's ai-infra-portfolio's job
- B2B / multi-tenant AI governance
- AI model training or fine-tuning tooling
- Cryptocurrency / wallet integration (even though some DID methods overlap)
