#!/usr/bin/env python3
from __future__ import annotations
import shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence'/'docker_smoke_result.txt'
OUT.parent.mkdir(exist_ok=True)
if not shutil.which('docker'):
    msg='NOT RUN: Docker CLI is not installed in this environment.'
    OUT.write_text(msg+'\n', encoding='utf-8'); print(msg); sys.exit(2)
cmd=['docker','compose','config']
proc=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
text=f"$ {' '.join(cmd)}\nexit_code={proc.returncode}\nSTDOUT:\n{proc.stdout[-4000:]}\nSTDERR:\n{proc.stderr[-4000:]}\n"
OUT.write_text(text, encoding='utf-8')
print(text)
sys.exit(proc.returncode)
