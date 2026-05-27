# ADR-0007: ollama Integration for `oya chat`

**Status**: Accepted
**Date**: 2026-05-27

## Context

Phase 3 goal: every conversation with a local LLM becomes a signed audit entry automatically.
`oya chat` needs to connect to a local LLM endpoint. Several options exist.

## Decision

Use **ollama** as the sole LLM backend for Phase 3, accessed via its HTTP REST API using
stdlib `urllib.request` only.

`oya chat` is an interactive REPL with three audit log levels:
- `none` — no logging (plain conversation)
- `summary` (default) — one entry per session at exit (model, turns, first prompt)
- `full` — one entry per prompt (human key) + one per response (ai key)

## Why ollama

| Factor | Choice |
|---|---|
| Local execution | ollama runs 100% on-device; matches the offline-first principle |
| Model availability | Ships Gemma3, Llama3, and 100+ models; easy `ollama pull` workflow |
| API simplicity | `POST /api/chat` with JSON — no SDK required |
| License | MIT |

## Why stdlib urllib (no ollama Python package)

The `ollama` Python package would simplify the code, but adds a transitive dependency
that could bring in `httpx` or other libraries. Using `urllib.request` directly keeps
the runtime dependency count unchanged and makes the HTTP contract explicit.

## Why `stream=False` in Phase 3

Streaming requires parsing newline-delimited JSON chunks, which adds ~40 lines of error-prone
buffer management. For Phase 3 (proof of concept), non-streaming is acceptable.
Streaming will be added in Phase 3.x once the basic flow is validated.

## Log level default: `summary`

Full per-turn logging (`full` mode) generates ~2 KB/turn. At 100 turns/day,
that is 73 MB/year of cryptographically chained entries. The `summary` default
caps this at one entry per session (~500 bytes), preserving the audit trail
without unbounded growth.

## Consequences

- `oya chat` requires ollama running at `localhost:11434` (or `--ollama-url`)
- No internet connection needed for conversations
- `--log-level full` is available for users who want complete per-turn audit trails
- llama.cpp, LM Studio, and OpenAI-compatible endpoints are deferred to Phase 3.x
