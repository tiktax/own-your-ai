# ADR-0001: Python as the base language for Phase 1

- **Status**: Accepted
- **Date**: 2026-05-26

## Context

own-your-ai inherits ECDSA signing and audit log code from [ai-infra-portfolio](https://github.com/tiktax/ai-infra-portfolio), which is written in Python. The project will eventually target mobile and embedded devices where Rust or Swift would be a better fit, but Phase 1 is a Mac-only foundation.

## Decision

Phase 1 uses **Python 3.11+** as the only implementation language.

## Consequences

**Positive**:
- Crypto code from ai-infra-portfolio copies directly with minimal changes
- The Python ecosystem provides mature libraries: `cryptography`, `pytest`, `ruff`
- CLI scaffolding is trivial via argparse and `[project.scripts]` entry points
- Easy onboarding for contributors

**Negative**:
- Python is a poor fit for eventual mobile / embedded targets
- Python's GIL is irrelevant at Phase 1 scale but will matter at Phase 3+ if we drive a local LLM in-process
- Distribution to non-developer end users will be friction (we'd need to ship a packaged binary or rely on `pipx`)

## When to revisit

When **either** of the following happens, open a follow-up ADR:

1. Mobile (iOS) integration becomes Phase priority → Swift bindings or Rust core become attractive
2. Phase 3 local-LLM integration shows Python is in the hot path of inference → Rust port of crypto + audit modules
