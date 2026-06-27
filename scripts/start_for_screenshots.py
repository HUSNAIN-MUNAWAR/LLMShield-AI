#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    print('Use scripts/capture_real_screenshots.py; it can start services automatically when dependencies are installed.')
    print('Manual mode: terminal 1: cd backend && uvicorn app.main:app --port 8000')
    print('Manual mode: terminal 2: cd frontend && npm run dev')
if __name__=='__main__': main()
