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

### T6 — Passphrase in environment variable (v0.3.1 disclosure)
**STRIDE**: Information Disclosure.

**Scenario**: The user sets `OWNYOURAI_PASSPHRASE=secret oya chat` in their shell. The passphrase is readable via `/proc/<pid>/environ` on Linux, may appear in shell history if set inline, and can be exposed in CI logs.

**v0.3.1 mitigations**:
- Warning printed to stderr when the env var is consumed: "passphrase read from OWNYOURAI_PASSPHRASE — ensure it is not logged"
- Documented here as a known risk

**Recommendation**: Use `OWNYOURAI_PASSPHRASE` only in isolated CI environments. For interactive use, let `oya` prompt via `getpass` (reads from `/dev/tty`, not shell history).

---

### T7 — Hash chain rebuild by keyholder (architectural limitation)
**STRIDE**: Tampering, Repudiation.

**Scenario**: An attacker who holds the private key (or has extracted it from the encrypted PEM via brute-force) deletes audit entries, re-signs replacements, and recomputes `prev_hash` forward from GENESIS. The resulting log passes `oya verify` with no failures.

**Current status**: The hash chain is **tamper-detectable** (casual edits without the key break the chain) but **not tamper-evident** in the cryptographic sense (the keyholder can rebuild a valid chain).

**v0.3.1 mitigation**: `oya audit anchor` — RFC 3161 Trusted Timestamping (opt-in). Submits the SHA-256 of `audit.jsonl` to a free TSA (freetsa.org by default). The returned TimeStampToken proves the log existed at a specific time, making backdating provably impossible even for the keyholder.

**Remaining gap**: `oya audit anchor` requires manual invocation. Automatic anchoring is deferred to Phase 4+ to preserve offline-first behavior.

---

### T8 — Conversation data leaving device via --ollama-url (v0.3.1 mitigation)
**STRIDE**: Information Disclosure.

**Scenario**: The user passes `--ollama-url https://remote-host.example.com` (deliberately or via a script), routing all conversation history to a remote server.

**v0.3.1 mitigation**: `_assert_local_url()` in `llm/ollama.py` resolves the hostname via DNS and prints a stderr warning if the IP is not a loopback address (127.x or ::1). The connection is not blocked — the warning is informational.

**Known gap**: DNS resolution can be spoofed (split-horizon DNS). A future version may enforce `--ollama-url` to loopback-only and require an explicit `--allow-remote` flag to override.

---

## Out of scope (Phase 1)

- Nation-state adversaries with physical device access AND coercion power
- Side-channel attacks on Secure Enclave (Phase 2 concern at earliest)
- Supply-chain attacks on `cryptography` upstream — tracked via dependabot in CI
- Post-quantum threats (Phase 6+)
