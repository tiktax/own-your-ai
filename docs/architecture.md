# Architecture

own-your-ai is structured as five layers. Each layer has a single concern; upper layers depend on lower layers, never the reverse.

## Layer diagram

```
┌────────────────────────────────────────────────────────────┐
│  L5: AI Inference         on-device LLM (Gemma3-class)     │  ← Phase 3
├────────────────────────────────────────────────────────────┤
│  L4: Identity (DID/SSI)   did:key / did:web / VC issuance  │  ← Phase 1 stub, Phase 2/5
├────────────────────────────────────────────────────────────┤
│  L3: Crypto / Audit       ECDSA P-256, JSONL hash chain    │  ← Phase 1 ✅
├────────────────────────────────────────────────────────────┤
│  L2: Keystore             passphrase PEM (Phase 1),        │  ← Phase 1 file, Phase 2 keychain
│                           macOS Keychain (Phase 2)         │
├────────────────────────────────────────────────────────────┤
│  L1: Hardware             user's own device (Mac/iPhone…)  │  ← out of project scope
└────────────────────────────────────────────────────────────┘
```

## Layer responsibilities

### L1 — Hardware
Outside the project's scope. own-your-ai assumes the user's own physical device. The threat model (see [threat-model.md](threat-model.md)) covers physical compromise of L1 but does not attempt to harden the hardware itself.

### L2 — Keystore
Holds private keys and the configuration that points to them.

- **Phase 1 (current)**: ECDSA P-256 keys stored as PEM files at `~/.ownyourai/keys/`, file mode 600. No passphrase yet — added in Phase 1 patch release.
- **Phase 2**: macOS Keychain wrapper (`crypto/keystore.py` currently stub). Secure Enclave evaluated separately (Secure Enclave supports P-256 but constrains key export).

### L3 — Crypto / Audit
Where the project earns its name. Every operation the user wants attributed is signed and chained.

- `crypto/signing.py` — ECDSA P-256 sign/verify, key fingerprint identification of operator type (AI vs HUMAN). Lifted from [ai-infra-portfolio Phase 5](https://github.com/tiktax/ai-infra-portfolio/tree/main/tools/trustless_audit/src).
- `audit/log.py` — append-only JSON Lines log, each entry has `prev_hash` referencing the sha256 of the previous canonical line. Tampering with any entry breaks the chain at that point.

The audit log is the single source of truth for "what did I do with my AI." Export from `oya export` is the GDPR Art.20 portability surface.

### L4 — Identity (DID/SSI)
The user's identifier, derived from L2 keys, portable across services.

- **Phase 1 (current)**: `identity/did.py` derives a `did:key` from the L2 public key. Stub — uses base64url multibase instead of the formal base58btc; sufficient for "this is what your DID would look like" but not yet interoperable with the wider DID ecosystem.
- **Phase 2**: replace stub with formal `did:key` (base58btc) and add `did:web` support.
- **Phase 5**: Verifiable Credentials issuance/verification on top of `did:key`.

### L5 — AI Inference
Where local LLM execution happens. Not in `src/` for Phase 1 — only diagrammed here.

- **Phase 3**: integration with a local LLM (Gemma3-class on Mac/iPhone). Each query/response pair will flow through L3 to become a signed audit entry.
- **Design intent**: L5 must call L3 to record what it did; L5 must never see L2 keys directly.

## Cross-cutting concerns

- **PII enforcement**: `examples/hooks/pii-guard.sh` is a `PreToolUse` hook for Claude Code that blocks accidental PII writes. Lives outside the Python package because it's an integration shim for a specific AI tool, not part of the core layered stack.
- **Privacy by default**: nothing in L1-L4 sends data over the network. Network access only appears at L5 if (and only if) the user opts in to a remote model — and that fact would itself become an L3 audit entry.

## Non-goals (Phase 1)

- Mobile UI / app shell — `oya` is a CLI on macOS
- Sync between devices — every device is independent in Phase 1
- Encrypted backups — relies on the user's existing backup hygiene
- M-of-N social recovery — Phase 4
- Post-quantum signing — Phase 6+
