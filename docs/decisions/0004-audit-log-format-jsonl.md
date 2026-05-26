# ADR-0004: Audit log format is JSON Lines with prev_hash chain

- **Status**: Accepted
- **Date**: 2026-05-26

## Context

The audit log is the project's single source of truth. Format options considered:

1. **JSON Lines** (one JSON object per line, append-only)
2. **SQLite database** with a signed-entries table
3. **A single large JSON array** rewritten on each append
4. **A purpose-built binary format** (CBOR, MessagePack)

We also need tamper detection without depending on external timestamp authorities or WORM storage (those exist in [ai-infra-portfolio Phase 5](https://github.com/tiktax/ai-infra-portfolio/tree/main/tools/trustless_audit) but are out of scope here per [Phase 8 design constraints](https://github.com/tiktax/ai-infra-portfolio/blob/main/docs/roadmap.md)).

## Decision

**JSON Lines (`.jsonl`) at `~/.ownyourai/audit.jsonl`**, each entry has a `prev_hash` field that references `sha256(canonical_json(previous_line))`. The first entry's `prev_hash` is the literal string `"GENESIS"`.

Each entry is also signed individually with ECDSA, so two independent integrity checks exist:
1. Per-entry: signature verification with the public key
2. Cross-entry: hash chain continuity from GENESIS to the latest entry

## Consequences

**Positive**:
- Trivially append-safe: open in O_APPEND, write one line, close
- `tail -f`, `grep`, `jq` all work without special tooling
- Streaming friendly — you don't need to load the whole log to verify one entry's signature
- Deleting / reordering any entry breaks the chain at that point — detected by `oya verify`
- Format is self-describing; future tools can read old logs

**Negative**:
- Larger on disk than a binary format (we accept this; logs at personal scale stay tiny)
- Inserting between entries is impossible by design (this is the intended behavior, not a bug)
- The chain is local-only — it does **not** prove anything to a third party who didn't witness the writes. That's what RFC 3161 timestamps and WORM storage solve, and they're deferred

## When to revisit

If the audit log exceeds ~100MB per user (extremely unlikely at personal scale, but Phase 3 local-LLM logging could change that), evaluate:
- SQLite for indexed queries
- Log rotation strategy (each rotated file gets a hash linking it to the next)
