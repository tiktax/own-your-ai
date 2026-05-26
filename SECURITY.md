# Security Policy

## Reporting a vulnerability

Please report security issues via **[GitHub Discussions](https://github.com/tiktax/own-your-ai/discussions) → Security category**.

If the issue is sensitive enough that public discussion is inappropriate, open a placeholder Discussions thread with **no technical detail** (e.g. "Need to discuss a security concern privately") and we will arrange a private channel from there.

## What counts as a vulnerability

- Forgery of audit log entries that pass `oya verify`
- Disclosure of private key material via documented `oya` commands
- Hash-chain bypass — modification of past entries that doesn't get flagged
- Anything in the [threat model](docs/threat-model.md) that the project claims to defend against but doesn't

## What does **not** count

- Threats outside the [threat model's scope](docs/threat-model.md) (e.g. nation-state physical compromise) — these are documented non-goals
- Issues that require already-compromised root access on the host
- The known Phase 1 gaps (passphrase-less PEM, no Keychain integration) — these are tracked openly in the [roadmap](docs/roadmap.md)

## Supported versions

Pre-1.0, only the latest release is supported.

| Version | Supported |
|---|---|
| 0.1.x | ✅ |
| older | ❌ |
