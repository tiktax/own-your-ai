# own-your-ai

> Your AI. Your data. Your rules.

**#MyAI #DigitalSovereignty #3rdWayAI**

---

## Vision

AI systems are increasingly mediating personal decisions — health, finance, relationships, identity. Yet the infrastructure running those systems is almost entirely external: cloud providers, platform operators, third-party model hosts.

**own-your-ai** is a third way: neither the platform's AI nor the enterprise's AI — your AI, running on your hardware, governed by your rules, with your data never leaving your control.

Aligned with [MyData Global](https://www.mydata.org/) principles. Differentiated by implementing the AI layer in code.

---

## Core Principles

| Principle | What it means |
|---|---|
| **Offline-first** | All inference runs locally. No data leaves the device by default. |
| **Individual as IdP** | You control your identity, credentials, and consent decisions. |
| **SSI/DID foundation** | Portable, verifiable identity — not owned by any platform. |
| **Data portability** | Your full AI history is exportable in open formats at any time. |
| **Cryptographic accountability** | Every AI decision is signed and auditable — by you, for you. |

---

## Technical Foundation

This project inherits cryptographic primitives from [ai-infra-portfolio](https://github.com/tiktax/ai-infra-portfolio):

| Component | Role |
|---|---|
| ECDSA P-256 + hash chain (Phase 5) | Personal AI decision audit trail |
| Post-quantum signing — ML-DSA-65 (Phase 5) | Future-proof identity layer |
| PII guard + display-time scrubbing (Phase 6a) | Privacy enforcement at the device level |

---

## Legal Framework

| Jurisdiction | Instrument | Right addressed |
|---|---|---|
| EU | AI Act (Art. 22) + GDPR (Art. 17, 20) | Right to explanation + data portability |
| US | EO 14110 + state AI bills | Transparency, opt-out rights |
| Japan | APPI 改正 (2022) + AI事業者ガイドライン | 要配慮個人情報 + 利用停止権 |

---

## Planned Capabilities

- **Mobile LLM**: Gemma3-class models run entirely on-device (technically feasible today)
- **Social recovery**: M-of-N key recovery for identity keys — no central authority required
- **SSI/DID credentials**: issuance and verification of self-sovereign identity credentials
- **Personal AI audit log**: portable, cryptographically signed, user-owned record of every AI decision

---

## Design Constraints

- **UX form factor is TBD**: smartphones are the current primary target, but the architecture is form-factor agnostic — the era chooses the UX
- **Japan regulatory gap**: Japan's AI governance framework is the most ambiguous of the three jurisdictions; this is a known blocker for Japan-specific implementation
- **Scope**: this project implements the AI layer; it does not duplicate MyData Global's work on data sharing agreements or consent management protocols

---

## Relationship to ai-infra-portfolio

| Project | Scope | User |
|---|---|---|
| [ai-infra-portfolio](https://github.com/tiktax/ai-infra-portfolio) | Organizational AI governance | Teams, compliance officers, CISOs |
| **own-your-ai** | Individual AI sovereignty | Everyone |

The governance primitives built for organizations (signed audit trails, privacy enforcement, ITSM-aligned change management) are the right primitives for individuals too — just pointed inward instead of outward.

---

## Tags

`#MyAI` `#DigitalSovereignty` `#3rdWayAI` `#SSI` `#DID` `#MyDataGlobal` `#OfflineAI` `#PersonalAI`

---

## Status

🔲 Pre-implementation. Architecture and legal framework defined. See [roadmap](https://github.com/tiktax/ai-infra-portfolio/blob/main/docs/roadmap.md) (Phase 8).
