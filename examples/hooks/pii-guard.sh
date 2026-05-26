#!/usr/bin/env bash
# pii-guard.sh — PreToolUse hook: detect PII patterns in commands and file writes
#
# Triggers on: Bash commands, Write/Edit file content
# Blocks: actual PII patterns (email, phone, My Number)
# Passes: keyword-only matches (e.g. "grep email src/") — no false positives
#
# Usage: configured as PreToolUse hook in ~/.claude/settings.json
# Test:
#   echo '{"tool_name":"Bash","tool_input":{"command":"echo user@example.com"}}' | bash pii-guard.sh
#   echo '{"tool_name":"Bash","tool_input":{"command":"grep email src/"}}' | bash pii-guard.sh

set -euo pipefail

PAYLOAD=$(cat)

PAYLOAD="$PAYLOAD" python3 <<'PYEOF'
import os, sys, json, re

PII_PATTERNS = [
    # Email address — requires @ and valid TLD (2+ chars)
    (re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'), 'EMAIL'),
    # Japanese phone number: 03-1234-5678, 090-1234-5678
    (re.compile(r'\b\d{2,4}-\d{2,4}-\d{4}\b'), 'PHONE'),
    # Japanese My Number: 1234-5678-9012 or 1234 5678 9012
    (re.compile(r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b'), 'MYNUMBER'),
]

# Template file extensions — always pass through (no false blocks)
TEMPLATE_SUFFIXES = ('.1password', '.example', '.template', '.tmpl', '.sample', '.dist')

raw = os.environ.get('PAYLOAD', '')
try:
    payload = json.loads(raw)
except Exception:
    sys.exit(0)

tool_name = payload.get('tool_name', '')

# Determine target string based on tool type
if tool_name == 'Bash':
    target = payload.get('tool_input', {}).get('command', '')
elif tool_name in ('Write', 'Edit'):
    file_path = payload.get('tool_input', {}).get('file_path', '')
    # Skip template/example files
    if any(file_path.endswith(suf) for suf in TEMPLATE_SUFFIXES):
        sys.exit(0)
    target = payload.get('tool_input', {}).get('content', '')
else:
    # Other tools (Read, etc.) — pass through
    sys.exit(0)

if not target:
    sys.exit(0)

# Check each PII pattern
for pattern, label in PII_PATTERNS:
    matches = pattern.findall(target)
    if matches:
        sample = matches[0] if len(matches[0]) <= 40 else matches[0][:37] + '...'
        tool_context = 'command' if tool_name == 'Bash' else 'content'
        sys.stderr.write(f'\n🚫 PII Guard: [{label}] pattern detected in {tool_name} {tool_context}\n')
        sys.stderr.write(f'   Detected: {sample} → [PII:{label}]\n')
        sys.stderr.write(f'   If this is intentional (test data, anonymized, etc.), review before proceeding.\n')
        sys.stderr.write(f'   Tip: Use placeholder values in code. Real PII should not appear in commands or file writes.\n')
        sys.exit(2)

sys.exit(0)
PYEOF

exit $?
