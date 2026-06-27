#!/usr/bin/env python3
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'evidence'; EVIDENCE.mkdir(exist_ok=True)
SKIP_DIRS={'.git','.venv','venv','node_modules','.next','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','dist','build','evidence'}
SKIP_SUFFIXES={'.png','.jpg','.jpeg','.gif','.pdf','.zip','.ico','.lock','.pyc'}
ALLOW_FILES={'.env.example'}
ALLOW_PATTERNS=['sk-demo','demo-token','dev-only-change-me','example.com','OPENAI_API_KEY','Authorization: Bearer demo']
PATTERNS=[
    ('openai_key', re.compile(r'sk-[A-Za-z0-9_\-]{20,}')),
    ('bearer_token', re.compile(r'Bearer\s+[A-Za-z0-9_\-\.]{16,}', re.I)),
    ('private_key', re.compile(r'-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----')),
    ('env_file', re.compile(r'^\.env$', re.I)),
    ('password_literal', re.compile(r'password\s*[:=]\s*["\'][^"\']{8,}["\']', re.I)),
]
findings=[]
if (ROOT/'.git').exists():
    proc=subprocess.run(
        ['git','ls-files','--cached','--others','--exclude-standard','-z'],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    candidates=[ROOT/item.decode('utf-8',errors='surrogateescape') for item in proc.stdout.split(b'\0') if item]
    tracked=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=False)
    tracked_paths=[item.decode('utf-8',errors='surrogateescape') for item in tracked.stdout.split(b'\0') if item]
else:
    candidates=list(ROOT.rglob('*'))
    tracked_paths=[]
for path in candidates:
    try: rel=path.relative_to(ROOT)
    except ValueError: continue
    if any(part in SKIP_DIRS for part in rel.parts): continue
    if path.is_dir(): continue
    if path.suffix.lower() in SKIP_SUFFIXES: continue
    if path.name == '.env': findings.append((str(rel),'env_file','committed .env file')); continue
    if path.name in ALLOW_FILES: continue
    try: text=path.read_text(encoding='utf-8', errors='ignore')
    except Exception: continue
    for name, pattern in PATTERNS:
        for m in pattern.finditer(text):
            snippet=m.group(0)[:120]
            if any(ap in snippet for ap in ALLOW_PATTERNS): continue
            # Allow documentation examples that are explicitly redacted.
            if 'REDACTED' in snippet or '<' in snippet: continue
            findings.append((str(rel), name, snippet))
for forbidden in ['.env','frontend/node_modules/','frontend/.next/','.venv/']:
    is_tracked=any(item == forbidden if not forbidden.endswith('/') else item.startswith(forbidden) for item in tracked_paths)
    if is_tracked:
        findings.append((forbidden,'hygiene','ignored local artifact is tracked by git'))
out=EVIDENCE/'secret_scan_result.txt'
if findings:
    out.write_text('FAILED secret scan\n'+'\n'.join(f'{a}: {b}: {c}' for a,b,c in findings[:100]), encoding='utf-8')
    print(out.read_text()); sys.exit(1)
out.write_text('PASSED: no committed secrets or forbidden build artifacts detected.\n', encoding='utf-8')
print(out.read_text())
