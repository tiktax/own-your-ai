# Legal Matrix

Maps relevant legal instruments to own-your-ai features. The right column says **which phase delivers the technical implementation**; "design only" means the law informs an ADR but no code yet.

## EU

| Instrument | Article | Right / Obligation | own-your-ai feature | Phase |
|---|---|---|---|---|
| AI Act | Art. 22 | Right to explanation for automated decisions | `oya audit show <N>` returns the full signed entry for any AI action | 1 ✅ |
| AI Act | Annex III | Risk classification for high-risk AI uses | Documented in `docs/decisions/` per feature | design only |
| GDPR | Art. 17 | Right to erasure | Local-only storage means erasure = file deletion; documented runbook deferred | 2 |
| GDPR | Art. 20 | Right to data portability | `oya export` outputs the full audit log in open JSON | 1 ✅ |
| GDPR | Art. 25 | Privacy by Design | Offline-first architecture; no telemetry; explicit opt-in for any future cloud features | architecture |

## United States

| Instrument | Section | Right / Obligation | own-your-ai feature | Phase |
|---|---|---|---|---|
| EO 14110 | §4.2 | AI transparency and safety reporting | Signed audit trail provides user-side transparency | 1 ✅ |
| CCPA | §1798.105 | Right to delete | Same as GDPR Art. 17 — local-only | 2 |
| CCPA | §1798.110 | Right to know what is collected | Audit log is the user's complete record of AI interactions | 1 ✅ |
| CPRA | §1798.140 | Sensitive personal information | `examples/hooks/pii-guard.sh` blocks email/phone/MyNumber/cards before they reach the AI | 1 ✅ (Claude Code only) |

## Japan

| Instrument | 該当条文 | Right / Obligation | own-your-ai feature | Phase |
|---|---|---|---|---|
| 改正個人情報保護法 (2022) | 第3条 | 要配慮個人情報の特別扱い | PII guard hook detects medical/identifier keywords | 1 ✅ (partial) |
| 改正個人情報保護法 | 第30条 | 利用停止権 | Local-only storage; user can stop at any time by removing keys | 1 ✅ |
| 改正個人情報保護法 | 第28条 | 第三者提供の制限 | No third-party transmission by default | architecture |
| AI事業者ガイドライン (2024) | §3 | 透明性確保 | Signed audit trail | 1 ✅ |
| AI事業者ガイドライン | §4 | アカウンタビリティ | Operator type (AI vs HUMAN) is cryptographically distinguishable via key fingerprint | 1 ✅ |

## Cross-jurisdiction summary

| Right | EU | US | JP | Phase 1 covers it? |
|---|---|---|---|---|
| Know what was decided | AI Act 22 | CCPA 1798.110 | AI GL §3 | **Yes** — `oya audit list/show` |
| Get a copy | GDPR 20 | CCPA 1798.100 | 個情法 開示 | **Yes** — `oya export` |
| Delete it | GDPR 17 | CCPA 1798.105 | 個情法 第30条 | **Yes** — `rm ~/.ownyourai/` (runbook in Phase 2) |
| Prove it was you (or your AI) | — | — | AI GL §4 | **Yes** — key fingerprint identifies operator |

## Non-coverage (honest gaps)

- **EU AI Act compliance reporting** — AI Act applies to providers/deployers, not personal users; the project does not generate the documentation a commercial provider needs
- **HIPAA / FERPA / financial sector rules** — not addressed; own-your-ai is for individuals, not regulated entities
- **CCPA business-side obligations** — out of scope, this is a tool for consumers
- **Cross-border data transfer** — moot because there is no transfer in Phase 1
