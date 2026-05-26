# Threat Model (Phase 1)

own-your-ai's threat model is shaped by its principles: the user owns the keys, the device, and the data. Most enterprise threat models assume an external adversary attacking shared infrastructure; ours assumes a personal device with realistic personal-scale threats.

Phase 1 uses a simplified STRIDE framing.

## Assets

| Asset | Why it matters |
|---|---|
| Private keys (`~/.ownyourai/keys/*_private_key.pem`) | Forging these forges any audit entry — the project's integrity guarantee dies |
| Audit log (`~/.ownyourai/audit.jsonl`) | Tampering with the past breaks the user's ability to reason about what their AI did |
| DID (derived from public key) | Loss of the keypair = loss of the identity |

## Threats and mitigations

### T1 — Physical device theft (Mac mini, laptop)
**STRIDE**: Tampering, Information Disclosure, Elevation of Privilege.

**Scenario**: Someone takes the Mac while it's unlocked or steals it and brute-forces the login.

**Phase 1 mitigations**:
- macOS file permissions (600) on private keys
- Documented expectation that the user enables FileVault

**Known gaps (Phase 2+)**:
- No passphrase on the private key PEM yet
- Keychain / Secure Enclave migration deferred to Phase 2

### T2 — Co-resident access (housemate, family member, shared workstation)
**STRIDE**: Spoofing, Tampering.

**Scenario**: Another person uses the same macOS account, or copies files from `~/.ownyourai/`.

**Phase 1 mitigations**:
- Same as T1 — file permissions assume separate macOS users

**Known gaps**:
- A passphrase-encrypted private key (Phase 1.x) blunts this significantly
- The audit log is currently world-readable to the OS user; encrypting it at rest is Phase 2

### T3 — Accidental cloud transmission (cloud AI tools, syncing services)
**STRIDE**: Information Disclosure.

**Scenario**: The user pastes a private prompt into a cloud LLM, or Time Machine/iCloud Drive syncs the keys folder.

**Phase 1 mitigations**:
- `~/.ownyourai/` is outside the standard iCloud Drive root
- `examples/hooks/pii-guard.sh` provides PII detection for one specific AI tool (Claude Code)

**Known gaps**:
- The PII guard is opt-in and only covers Claude Code; other AI tools have no enforcement
- No filesystem-level "do not sync" attribute applied yet

### T4 — Backup compromise
**STRIDE**: Information Disclosure.

**Scenario**: A backup (Time Machine, cloud) is stolen or accessed by the backup provider.

**Phase 1 mitigations**:
- Documented expectation that the user encrypts backups

**Known gaps**:
- No native encryption inside own-your-ai; relies entirely on user backup hygiene
- Passphrase-protected keys (Phase 1.x) would extend defense-in-depth into backups

### T5 — Accidental git commit of secrets
**STRIDE**: Information Disclosure.

**Scenario**: The user clones own-your-ai source, adds their `audit.jsonl` to it for testing, and commits/pushes.

**Phase 1 mitigations**:
- `.gitignore` excludes `*.pem`, `audit_logs/`, `.env*`
- `gitleaks` runs in CI and pre-commit
- `detect-private-key` pre-commit hook catches PEM headers

## Out of scope (Phase 1)

- Nation-state adversaries with physical device access AND coercion power
- Side-channel attacks on Secure Enclave (Phase 2 concern at earliest)
- Supply-chain attacks on `cryptography` upstream — tracked via dependabot in CI
- Post-quantum threats (Phase 6+)
