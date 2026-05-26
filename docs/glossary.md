# Glossary

Plain-language definitions for the terms used in own-your-ai docs and code.

| Term | One-line definition |
|---|---|
| **AI Act (EU)** | EU regulation entering effect 2024–2026 that classifies AI uses by risk and imposes transparency / oversight requirements |
| **APPI (改正個人情報保護法)** | Japan's Act on the Protection of Personal Information, last major revision 2022 |
| **CCPA / CPRA** | California Consumer Privacy Act (2020) and California Privacy Rights Act (2023) — US-state-level privacy laws |
| **DID** | Decentralized Identifier — a self-owned, platform-independent identifier (`did:key:...`, `did:web:example.com`) |
| **did:key** | A DID method that derives the identifier directly from a public key (no registry needed) |
| **did:web** | A DID method that resolves via HTTPS to a DID document on a domain you control |
| **ECDSA P-256** | Elliptic Curve Digital Signature Algorithm on the NIST P-256 curve — the signing algorithm own-your-ai uses |
| **EO 14110** | US Executive Order on Safe, Secure, and Trustworthy AI (October 2023) |
| **GDPR** | EU General Data Protection Regulation (2018) |
| **GENESIS** | The literal string used as `prev_hash` for the first entry in an audit log |
| **Hash chain** | Each audit entry includes the hash of the previous entry, so deleting or reordering breaks the chain |
| **IdP** | Identity Provider — the system that vouches for "who you are." own-your-ai's principle: the individual is their own IdP |
| **JSON Lines (JSONL)** | A file format where each line is an independent JSON object — easy to append, grep, and stream |
| **Key fingerprint** | sha256 of a public key PEM — used to identify which key signed an entry without disclosing the key |
| **MyData Global** | A non-profit advancing human-centric personal data principles (https://mydata.org) |
| **MyNumber (マイナンバー)** | Japan's individual taxpayer/social ID number — 12 digits, classified as 要配慮個人情報 |
| **PEM** | Base64-encoded key format with `-----BEGIN ... KEY-----` headers — the standard private/public key file format |
| **PII** | Personally Identifiable Information — emails, phone numbers, IDs etc. |
| **SSI** | Self-Sovereign Identity — the umbrella concept where the individual controls their own identifiers and credentials |
| **STRIDE** | A threat modeling framework: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege |
| **TRiSM** | Trust, Risk and Security Management (Gartner term) — a framework own-your-ai aligns with at the individual scale |
| **VC** | Verifiable Credential — a tamper-evident claim signed by an issuer about a subject (W3C spec) |
| **要配慮個人情報** | Japan's "special-care-required personal information" category under APPI (race, religion, medical, criminal record, MyNumber, etc.) |
