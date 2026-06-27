from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.services.risk_scoring import risk_band
from app.services.scanner import ScannerService
from app.services.target_clients import TargetConfig

ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def run_ci(target: str, attack_packs: list[str], fail_on: str, output: Path) -> int:
    safe_mode = target.endswith("safe")
    target_config = TargetConfig(id=target, name=target, type="mock_llm", safe_mode=safe_mode)
    result = ScannerService().run_scan(target_config, attack_packs)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.__dict__, indent=2), encoding="utf-8")
    worst = "low"
    for finding in result.findings:
        if ORDER[finding["severity"]] > ORDER[worst]:
            worst = finding["severity"]
    return 1 if ORDER[worst] >= ORDER[fail_on] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run LLMShield AI in CI fail-threshold mode.")
    parser.add_argument("--target", default="mock-unsafe")
    parser.add_argument("--attack-packs", default="prompt_injection,jailbreak,rag_poisoning")
    parser.add_argument("--fail-on", default="high", choices=["low", "medium", "high", "critical"])
    parser.add_argument("--output", default="sample_outputs/reports/ci_report.json")
    args = parser.parse_args(argv)
    packs = [p.strip() for p in args.attack_packs.split(",") if p.strip()]
    return run_ci(args.target, packs, args.fail_on, Path(args.output))


if __name__ == "__main__":
    sys.exit(main())
