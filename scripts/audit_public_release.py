#!/usr/bin/env python3
"""Best-effort public source audit; no hard-coded private identifiers."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
    "absolute user profile path":re.compile(r"(?i)(?:[A-Z]:\\Users\\(?!example\\|somebody\\|test\\)[^\\\s\"']+\\|/Users/(?!example/|test/)[A-Za-z0-9._-]+/|/home/(?!example/|test/)[A-Za-z0-9._-]+/)"),
    "credential literal": re.compile(r"(?i)(?:sk-(?:proj-)?[a-z0-9_-]{32,}|gh[opusr]_[a-z0-9]{32,}|AIza[a-z0-9_-]{35})"),
    "private local path":re.compile(r"(?i)[A-Z]:\\(?:AI|Projects|Documents|Desktop)\\[A-Za-z0-9._-]+\\"),
    "IPv4 literal": re.compile(r"(?<![\w\\])(?:\d{1,3}\.){3}\d{1,3}(?!\w)"),
}
errors=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or p.name == 'audit_public_release.py' or any(x in p.parts for x in ('__pycache__','.pytest_cache','.git')):continue
    body=p.read_text('utf-8-sig',errors='replace')
    for label, pat in PATTERNS.items():
        if pat.search(body): errors.append(f'{p.relative_to(ROOT)}: {label}')
if errors:raise SystemExit('PRIVACY AUDIT FAILED:\n' + '\n'.join(errors))
print('PRIVACY AUDIT PASS: no apparent personal paths, credentials, or literal IPs. Manual review remains required.')
