#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NAMES=[
    '01-login.png',
    '02-dashboard.png',
    '03-targets.png',
    '04-attack-packs.png',
    '05-scans.png',
    '06-findings.png',
    '07-reports.png',
    '08-settings-providers.png',
    '09-audit-logs.png',
    '10-docs.png',
]
errors=[]
for base in [ROOT/'sample_outputs'/'screenshots', ROOT/'frontend'/'public'/'screenshots']:
    for name in NAMES:
        path=base/name
        if not path.exists(): errors.append(f'missing {path}'); continue
        try:
            with Image.open(path) as img:
                img.verify()
                if img.format!='PNG': errors.append(f'not PNG {path}')
        except Exception as exc: errors.append(f'invalid {path}: {exc}')
method=(ROOT/'sample_outputs'/'screenshots'/'SCREENSHOT_METHOD.md')
if not method.exists(): errors.append('missing SCREENSHOT_METHOD.md')
out=ROOT/'evidence'/'screenshot_result.txt'; out.parent.mkdir(exist_ok=True)
if errors:
    text='FAILED screenshot verification\n'+'\n'.join(errors)
    out.write_text(text+'\n', encoding='utf-8'); print(text); sys.exit(1)
text='PASSED: all required screenshot PNG files exist and are valid.\n'+method.read_text(encoding='utf-8')
out.write_text(text, encoding='utf-8'); print(text)
