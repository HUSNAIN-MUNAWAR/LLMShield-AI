from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs" / "animation" / "security_scan_sequence.json"
REEL = ROOT / "frontend" / "public" / "animation" / "security-scan-reel.html"


def test_security_animation_compares_vulnerable_and_safe_modes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_security_animation.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": "backend"},
        check=True,
        capture_output=True,
        text=True,
    )
    assert "vulnerable failures:" in result.stdout

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reel = REEL.read_text(encoding="utf-8")
    assert manifest["model"]["model"] == "mock-deterministic"
    assert manifest["model"]["deterministic"] is True
    assert manifest["source"]["pack_test_counts"] == {"prompt_injection": 4, "secret_leakage": 4, "tool_misuse": 4}
    assert manifest["comparison"]["vulnerable_mode"]["total_tests"] == 12
    assert manifest["comparison"]["vulnerable_mode"]["failed_tests"] > 0
    assert manifest["comparison"]["safe_mode"]["failed_tests"] == 0
    assert len(manifest["events"]) == 7
    assert "authorized synthetic target" in reel.lower()
