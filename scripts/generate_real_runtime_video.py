"""Capture the real LLMShield MockLLM scanner as an inspectable MP4."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.attack_pack_loader import AttackPackLoader  # noqa: E402
from app.services.scanner import ScannerService, severity_distribution  # noqa: E402
from app.services.target_clients import TargetConfig  # noqa: E402


SOURCE = ROOT / "demo_data" / "animation" / "synthetic_security_scan.json"
OUTPUT_ROOT = ROOT / "docs" / "animation" / "runtime-evidence"
VIDEO_PATH = OUTPUT_ROOT / "llmshield-runtime.mp4"
POSTER_PATH = OUTPUT_ROOT / "llmshield-runtime-poster.png"
FINDINGS_PATH = OUTPUT_ROOT / "llmshield-findings.csv"
SUMMARY_PATH = OUTPUT_ROOT / "llmshield-runtime-summary.json"
FRAMES_PER_EVENT = 5
FPS = 5


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display(value: object) -> str:
    return str(value).encode("ascii", "replace").decode("ascii")


def put_text(canvas: np.ndarray, value: object, x: int, y: int, scale: float = 0.56, color: tuple[int, int, int] = (220, 232, 236), thickness: int = 1) -> None:
    cv2.putText(canvas, display(value), (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def scan_runtime() -> dict[str, object]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    pack_ids = list(source["attack_pack_ids"])
    loader = AttackPackLoader()
    packs = loader.get_by_ids(pack_ids)
    scanner = ScannerService(loader=loader)
    vulnerable_target = TargetConfig(**source["target"], safe_mode=False)
    safe_target = TargetConfig(**source["target"], safe_mode=True)
    vulnerable = scanner.run_scan(vulnerable_target, pack_ids, scan_id="real-runtime-vulnerable")
    safe = scanner.run_scan(safe_target, pack_ids, scan_id="real-runtime-safe")
    rows: list[dict[str, object]] = []
    for mode, result in (("vulnerable", vulnerable), ("safe", safe)):
        for index, finding in enumerate(result.findings, start=1):
            rows.append(
                {
                    "mode": mode,
                    "finding_index": index,
                    "attack_pack_id": finding["attack_pack_id"],
                    "test_id": finding["test_id"],
                    "detector_name": finding["detector_name"],
                    "passed": finding["passed"],
                    "severity": finding["severity"],
                    "risk_score": finding["risk_score"],
                    "confidence": finding["confidence"],
                    "provider": "mock",
                    "model": "mock-deterministic",
                    "response": finding["response"],
                    "evidence": finding["evidence"],
                    "mitigation": finding["mitigation"],
                }
            )
    return {
        "source": {
            "path": str(SOURCE.relative_to(ROOT)),
            "fixture": source["fixture_id"],
            "sha256": file_sha256(SOURCE),
            "target": source["target"],
            "attack_pack_ids": pack_ids,
            "pack_test_counts": {pack.id: len(pack.tests) for pack in packs},
        },
        "model": {
            "provider": "mock",
            "model": "mock-deterministic",
            "implementation": "backend/app/services/providers/mock_provider.py::MockLLMProvider",
            "learned_checkpoint": None,
            "deterministic": True,
            "external_endpoint": False,
            "claim_boundary": "Synthetic defensive scan using a rule-backed mock target; not live LLM or security certification evidence.",
        },
        "vulnerable": {
            "safe_mode": False,
            "status": vulnerable.status,
            "total_tests": vulnerable.total_tests,
            "passed_tests": vulnerable.passed_tests,
            "failed_tests": vulnerable.failed_tests,
            "risk_score": vulnerable.risk_score,
            "severity_distribution": severity_distribution(vulnerable.findings),
        },
        "safe": {
            "safe_mode": True,
            "status": safe.status,
            "total_tests": safe.total_tests,
            "passed_tests": safe.passed_tests,
            "failed_tests": safe.failed_tests,
            "risk_score": safe.risk_score,
            "severity_distribution": severity_distribution(safe.findings),
        },
        "rows": rows,
    }


def evidence_lines(run: dict[str, object], event_index: int) -> list[str]:
    source = run["source"]
    vulnerable = run["vulnerable"]
    safe = run["safe"]
    if event_index == 0:
        return [f"fixture: {source['fixture']}", f"packs: {len(source['attack_pack_ids'])}", f"tests: {sum(source['pack_test_counts'].values())}", f"sha256: {source['sha256'][:28]}..."]
    if event_index == 1:
        return ["provider: mock", "model: mock-deterministic", "external endpoint: false", "authorized local target only"]
    if event_index == 2:
        return [f"responses inspected: {vulnerable['total_tests']}", f"failed: {vulnerable['failed_tests']}", f"passed: {vulnerable['passed_tests']}", "redaction and detector evidence retained"]
    if event_index == 3:
        return [f"findings: {vulnerable['failed_tests']}", *[f"{key}: {value}" for key, value in vulnerable["severity_distribution"].items()]]
    if event_index == 4:
        return [f"risk score: {vulnerable['risk_score']}", f"status: {vulnerable['status']}", "risk aggregation from actual finding scores"]
    if event_index == 5:
        return [f"safe failures: {safe['failed_tests']}", f"safe risk: {safe['risk_score']}", "same packs, safe_mode refusal behavior"]
    return ["findings CSV: one row per scan result", "JSON report: source and output hashes", "no live system was contacted"]


def render_frame(run: dict[str, object], event_index: int, frame_number: int, frame_count: int) -> np.ndarray:
    titles = ["Attack packs loaded", "Mock provider executed", "Detectors inspected responses", "Findings preserved", "Risk aggregated", "Safe mode compared", "Evidence exported"]
    details = [
        "The real scanner loads the versioned YAML defensive test packs.",
        "TargetClient sends every authorized test to the local deterministic provider.",
        "Each actual response is evaluated by the configured detector registry.",
        "Failed tests become redacted findings with evidence and mitigation.",
        "The risk scorer aggregates the finding scores into a scan-level result.",
        "The same attack suite is rerun with safe refusal behavior enabled.",
        "Every finding and comparison result is retained in machine-readable evidence.",
    ]
    canvas = np.full((720, 1280, 3), (10, 13, 28), dtype=np.uint8)
    put_text(canvas, "LLMShield AI - REAL LOCAL SCANNER RUNTIME", 40, 48, 0.96, (240, 243, 248), 2)
    put_text(canvas, f"event {event_index + 1}/7  |  frame {frame_number}/{frame_count}", 40, 80, 0.56, (155, 168, 186))
    cv2.rectangle(canvas, (34, 108), (820, 660), (48, 60, 80), 2)
    cv2.rectangle(canvas, (852, 108), (1240, 660), (48, 60, 80), 2)
    put_text(canvas, titles[event_index], 60, 158, 0.78, (115, 167, 255), 2)
    put_text(canvas, details[event_index], 60, 194, 0.52, (210, 222, 230))
    for index, line in enumerate(evidence_lines(run, event_index)):
        put_text(canvas, line, 66, 260 + index * 38, 0.55, (221, 231, 235))
    model = run["model"]
    panel = [
        "EXECUTED PATH",
        "ScannerService + MockLLM",
        f"provider: {model['provider']}",
        "learned checkpoint: none",
        "",
        "COMPARISON",
        f"vulnerable risk: {run['vulnerable']['risk_score']}",
        f"safe risk: {run['safe']['risk_score']}",
        f"safe failures: {run['safe']['failed_tests']}",
        "",
        "CLAIM BOUNDARY",
        "synthetic defensive target",
        "mock provider, not live LLM",
        "authorized local testing only",
    ]
    for index, line in enumerate(panel):
        heading = index in {0, 5, 10}
        put_text(canvas, line, 882, 158 + index * 31, 0.54 if not heading else 0.61, (220, 232, 236) if not heading else (115, 167, 255), 1 if not heading else 2)
    put_text(canvas, "real scanner output | mock model boundary | no fabricated security claim", 40, 695, 0.52, (155, 168, 186))
    return canvas


def main() -> None:
    run = scan_runtime()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(VIDEO_PATH), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (1280, 720))
    if not writer.isOpened():
        raise RuntimeError(f"unable to open video writer for {VIDEO_PATH}")
    frame_count = 7 * FRAMES_PER_EVENT
    first_frame: np.ndarray | None = None
    frame_number = 0
    try:
        for event_index in range(7):
            for _ in range(FRAMES_PER_EVENT):
                frame_number += 1
                frame = render_frame(run, event_index, frame_number, frame_count)
                first_frame = first_frame if first_frame is not None else frame.copy()
                writer.write(frame)
    finally:
        writer.release()
    if first_frame is None:
        raise RuntimeError("no runtime frames were produced")
    cv2.imwrite(str(POSTER_PATH), first_frame)
    fields = ["mode", "finding_index", "attack_pack_id", "test_id", "detector_name", "passed", "severity", "risk_score", "confidence", "provider", "model", "response", "evidence", "mitigation"]
    with FINDINGS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer_csv = csv.DictWriter(handle, fieldnames=fields)
        writer_csv.writeheader()
        writer_csv.writerows(run["rows"])
    report = {
        "run_type": "llmshield_real_local_mock_scanner_video",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "py -3.12 -u scripts/generate_real_runtime_video.py",
        "source": run["source"],
        "model": run["model"],
        "vulnerable": run["vulnerable"],
        "safe": run["safe"],
        "runtime": {"python": platform.python_version(), "opencv": cv2.__version__, "numpy": np.__version__, "platform": platform.platform(), "device": "cpu"},
        "outputs": {
            "video": str(VIDEO_PATH.relative_to(ROOT)),
            "poster": str(POSTER_PATH.relative_to(ROOT)),
            "findings_csv": str(FINDINGS_PATH.relative_to(ROOT)),
            "sha256": {str(path.relative_to(ROOT)): file_sha256(path) for path in (VIDEO_PATH, POSTER_PATH, FINDINGS_PATH)},
        },
        "interpretation": [
            "This is a real local ScannerService run over the repository's authorized synthetic target and attack packs.",
            "The provider is deterministic MockLLM; no live endpoint, OpenAI key, Ollama model, or learned checkpoint was used.",
            "Vulnerable and safe-mode findings are preserved per test in the CSV.",
            "The result demonstrates defensive scanner behavior, not real-world LLM security coverage or certification.",
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"video": str(VIDEO_PATH), "poster": str(POSTER_PATH), "summary": str(SUMMARY_PATH), "finding_rows": len(run["rows"])}, indent=2))


if __name__ == "__main__":
    main()
