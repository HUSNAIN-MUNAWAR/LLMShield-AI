"""Generate a deterministic LLMShield scan-comparison animation and manifest."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.attack_pack_loader import AttackPackLoader  # noqa: E402
from app.services.scanner import ScannerService, severity_distribution  # noqa: E402
from app.services.target_clients import TargetConfig  # noqa: E402


SOURCE = ROOT / "demo_data" / "animation" / "synthetic_security_scan.json"
MANIFEST = ROOT / "docs" / "animation" / "security_scan_sequence.json"
REEL = ROOT / "frontend" / "public" / "animation" / "security-scan-reel.html"


def stable_finding(finding: dict[str, object]) -> dict[str, object]:
    return {
        "attack_pack_id": finding["attack_pack_id"],
        "test_id": finding["test_id"],
        "test_name": finding["test_name"],
        "detector_name": finding["detector_name"],
        "passed": finding["passed"],
        "severity": finding["severity"],
        "risk_score": finding["risk_score"],
        "category": finding["category"],
        "confidence": finding["confidence"],
        "evidence": finding["evidence"],
        "mitigation": finding["mitigation"],
        "provider": "mock",
        "model": "mock-deterministic",
    }


def run_scan(scanner: ScannerService, target: TargetConfig, pack_ids: list[str], scan_id: str):
    # The production scanner writes JSONL evidence. The generator keeps the
    # checked-in manifest stable by capturing the same in-memory result without
    # creating a run-specific log file.
    scanner._append_jsonl = lambda *_args: None
    return scanner.run_scan(target, pack_ids, scan_id=scan_id)


def build_manifest() -> dict[str, object]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    pack_ids = list(source["attack_pack_ids"])
    loader = AttackPackLoader()
    packs = loader.get_by_ids(pack_ids)
    scanner = ScannerService(loader=loader)
    vulnerable_target = TargetConfig(**source["target"], safe_mode=False)
    safe_target = TargetConfig(**source["target"], safe_mode=True)
    vulnerable = run_scan(scanner, vulnerable_target, pack_ids, "animation-vulnerable")
    safe = run_scan(scanner, safe_target, pack_ids, "animation-safe")
    vulnerable_findings = [stable_finding(finding) for finding in vulnerable.findings]
    failed = [finding for finding in vulnerable_findings if not finding["passed"]]
    pack_counts = {pack.id: len(pack.tests) for pack in packs}
    source_bytes = SOURCE.read_bytes()

    return {
        "schema_version": "1.0",
        "fixture": source["fixture_id"],
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "bytes": len(source_bytes),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "synthetic": True,
            "target": source["target"],
            "attack_pack_ids": pack_ids,
            "pack_test_counts": pack_counts,
        },
        "model": {
            "provider": "mock",
            "model": "mock-deterministic",
            "implementation": "backend/app/services/target_clients.py::TargetClient -> backend/app/services/providers/mock_provider.py::MockLLMProvider",
            "scanner": "backend/app/services/scanner.py::ScannerService",
            "detector_registry": "backend/app/services/detectors.py::run_detector",
            "risk_scoring": "backend/app/services/risk_scoring.py::aggregate_scan_score",
            "redaction": "backend/app/core/redaction.py::redact_text",
            "deterministic": True,
            "claim_boundary": "Synthetic defensive scan using a rule-backed mock target; not a real endpoint or security certification.",
        },
        "comparison": {
            "vulnerable_mode": {
                "safe_mode": False,
                "status": vulnerable.status,
                "total_tests": vulnerable.total_tests,
                "failed_tests": vulnerable.failed_tests,
                "passed_tests": vulnerable.passed_tests,
                "risk_score": vulnerable.risk_score,
                "severity_distribution": severity_distribution(vulnerable.findings),
            },
            "safe_mode": {
                "safe_mode": True,
                "status": safe.status,
                "total_tests": safe.total_tests,
                "failed_tests": safe.failed_tests,
                "passed_tests": safe.passed_tests,
                "risk_score": safe.risk_score,
                "severity_distribution": severity_distribution(safe.findings),
            },
            "failed_finding_count": len(failed),
            "detector_distribution": dict(Counter(finding["detector_name"] for finding in failed)),
        },
        "findings_preview": failed[:5],
        "events": [
            {"id": "packs", "short": "Packs", "title": "Versioned attack packs loaded", "detail": "The local scan selects prompt injection, secret leakage, and tool misuse test packs.", "metric": f"{len(pack_ids)} packs · {sum(pack_counts.values())} tests", "status": "loaded"},
            {"id": "provider", "short": "Provider", "title": "Mock target receives prompts", "detail": "TargetClient routes every authorized test to the deterministic MockLLM provider without network access.", "metric": "mock-deterministic · safe mode switchable", "status": "executed"},
            {"id": "detectors", "short": "Detect", "title": "Detectors inspect responses", "detail": "Each response passes through the configured detector and retains matched evidence and mitigation guidance.", "metric": f"{len(vulnerable_findings)} responses · redaction enabled", "status": "inspected"},
            {"id": "findings", "short": "Findings", "title": "Unsafe behavior becomes evidence", "detail": "The vulnerable-mode target produces findings across secrets, tool use, and injection behavior.", "metric": f"{vulnerable.failed_tests} failed · {vulnerable.passed_tests} passed", "status": "flagged"},
            {"id": "risk", "short": "Risk", "title": "Risk is aggregated", "detail": "The scorer combines the highest-risk findings into a scan-level score and severity distribution.", "metric": f"risk {vulnerable.risk_score} · {vulnerable.severity_distribution if hasattr(vulnerable, 'severity_distribution') else severity_distribution(vulnerable.findings)}", "status": "scored"},
            {"id": "safe", "short": "Safe", "title": "Safe mode is compared", "detail": "The same synthetic suite is replayed with refusal behavior enabled to make the control effect visible.", "metric": f"failed {safe.failed_tests} · risk {safe.risk_score}", "status": "compared"},
            {"id": "report", "short": "Report", "title": "Redacted report is ready", "detail": "Findings retain test identity, detector evidence, severity, confidence, and remediation without requiring a real target.", "metric": "JSON · Markdown · HTML · PDF-ready", "status": "exported"},
        ],
    }


def reel_html(manifest: dict[str, object]) -> str:
    sequence = json.dumps(manifest, indent=2, sort_keys=True).replace("</", "<\\/")
    return dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>LLMShield AI — Security scan reference reel</title>
          <style>
            :root {{ color-scheme: dark; --ink: #f0f3f8; --muted: #9ba8ba; --line: #303c50; --accent: #73a7ff; --danger: #ff7f91; --safe: #71ddb5; }}
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; min-width: 320px; background: radial-gradient(circle at 85% 0%, #382748 0, #101521 55%, #080b12 100%); color: var(--ink); font: 15px/1.5 Inter, ui-sans-serif, system-ui, sans-serif; }}
            .reel {{ max-width: 1180px; margin: 0 auto; padding: 42px 28px 34px; }}
            .eyebrow {{ color: var(--accent); font-size: 12px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }}
            h1 {{ max-width: 820px; margin: 8px 0 10px; font-size: clamp(28px, 5vw, 52px); line-height: 1.02; letter-spacing: -.04em; }}
            .lede {{ max-width: 790px; margin: 0; color: var(--muted); font-size: 17px; }}
            .model-line {{ display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 22px; color: var(--muted); font-size: 12px; }}
            .model-line span::before {{ content: "•"; color: var(--accent); margin-right: 8px; }}
            .stage {{ margin-top: 36px; overflow: hidden; border: 1px solid var(--line); border-radius: 22px; background: linear-gradient(145deg, rgba(30,35,57,.94), rgba(10,13,22,.97)); box-shadow: 0 22px 60px rgba(0,0,0,.28); }}
            svg {{ display: block; width: 100%; height: auto; min-height: 300px; }}
            .route {{ fill: none; stroke: #3a4560; stroke-width: 4; stroke-linecap: round; stroke-dasharray: 7 12; }}
            .station circle {{ fill: #0a111d; stroke: #4a5873; stroke-width: 3; transition: fill .25s ease, stroke .25s ease, transform .25s ease; transform-origin: center; }}
            .station text {{ fill: #a4b1c4; font-size: 14px; text-anchor: middle; }}
            .station .index {{ fill: #d8dfeb; font-size: 13px; font-weight: 700; }}
            .station.active circle {{ fill: #233e70; stroke: var(--accent); transform: scale(1.1); }}
            .station.active text {{ fill: var(--ink); }}
            .station.done circle {{ fill: #1d2e4b; stroke: #6d84b0; }}
            .token {{ fill: var(--accent); stroke: #e1ebff; stroke-width: 3; filter: drop-shadow(0 0 12px rgba(115,167,255,.65)); }}
            .token-label {{ fill: #0d1a38; font-size: 10px; font-weight: 800; text-anchor: middle; }}
            .panel {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 18px; padding: 22px 24px 24px; border-top: 1px solid var(--line); }}
            .panel h2 {{ margin: 0 0 3px; font-size: 24px; letter-spacing: -.02em; }}
            .panel p {{ margin: 0; color: var(--muted); }}
            .metric {{ color: var(--accent); font-size: 13px; font-weight: 700; text-align: right; }}
            .controls {{ display: flex; gap: 8px; margin-top: 16px; }}
            button {{ border: 1px solid #4d5e7e; border-radius: 999px; padding: 9px 15px; background: #18233b; color: var(--ink); font: inherit; cursor: pointer; }}
            button:hover, button:focus-visible {{ border-color: var(--accent); outline: 2px solid rgba(115,167,255,.35); outline-offset: 2px; }}
            .timeline {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 7px; margin-top: 18px; }}
            .timeline button {{ min-height: 60px; border-radius: 12px; padding: 8px; color: var(--muted); text-align: left; font-size: 12px; }}
            .timeline button[aria-current="step"] {{ border-color: var(--accent); background: #243c6a; color: var(--ink); }}
            .timeline strong {{ display: block; color: inherit; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }}
            .disclaimer {{ margin-top: 20px; color: var(--muted); font-size: 12px; }}
            @media (max-width: 760px) {{ .reel {{ padding: 28px 16px; }} .panel {{ grid-template-columns: 1fr; }} .metric {{ text-align: left; }} .timeline {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} svg {{ min-height: 420px; }} }}
            @media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; }} }}
          </style>
        </head>
        <body>
          <main class="reel" aria-labelledby="title">
            <div class="eyebrow">LLMShield AI · production reference reel</div>
            <h1 id="title">Find the failure. Compare the control.</h1>
            <p class="lede">A deterministic 12-case defensive scan shows how attack packs, a model provider, detectors, redaction, and risk scoring become an auditable security decision.</p>
            <div class="model-line" aria-label="Model and data boundary"><span id="model-name"></span><span id="source-name"></span><span>authorized synthetic target only</span></div>
            <section class="stage" aria-label="Animated security scan sequence">
              <svg viewBox="0 0 1210 390" role="img" aria-labelledby="diagram-title diagram-description">
                <title id="diagram-title">Animated LLMShield scan stages</title>
                <desc id="diagram-description">A scan token travels through attack pack loading, model execution, detectors, findings, risk aggregation, safe mode comparison, and report evidence.</desc>
                <path class="route" d="M 80 190 C 220 82, 360 82, 510 190 S 800 298, 1130 100" />
                <g id="stations"></g>
                <g aria-hidden="true"><circle id="token" class="token" cx="80" cy="190" r="22"></circle><text id="token-label" class="token-label" x="80" y="194">SCAN</text></g>
              </svg>
              <div class="panel" aria-live="polite"><div><h2 id="event-title"></h2><p id="event-detail"></p></div><div id="event-metric" class="metric"></div></div>
            </section>
            <div class="controls"><button id="toggle" type="button">Pause</button><button id="replay" type="button">Replay</button></div>
            <div id="timeline" class="timeline" role="list" aria-label="Animation stages"></div>
            <p class="disclaimer">Synthetic fixture · deterministic MockLLM · defensive authorized testing only · no external target is contacted.</p>
          </main>
          <script>
            const sequence = {sequence};
            const events = sequence.events;
            const points = [[80,190],[230,96],[380,96],[530,190],[680,284],[830,284],[980,190]];
            const stations = document.getElementById('stations'), timeline = document.getElementById('timeline');
            const token = document.getElementById('token'), tokenLabel = document.getElementById('token-label');
            const title = document.getElementById('event-title'), detail = document.getElementById('event-detail'), metric = document.getElementById('event-metric');
            const toggle = document.getElementById('toggle');
            let current = 0, started = performance.now(), playing = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            const duration = 1850;
            points.forEach((point, index) => {{
              const group = document.createElementNS('http://www.w3.org/2000/svg', 'g'); group.classList.add('station');
              group.innerHTML = `<circle cx="${{point[0]}}" cy="${{point[1]}}" r="30"></circle><text class="index" x="${{point[0]}}" y="${{point[1] + 5}}">${{index + 1}}</text><text x="${{point[0]}}" y="${{point[1] + 57}}">${{events[index].short}}</text>`;
              stations.appendChild(group);
            }});
            events.forEach((event, index) => {{
              const item = document.createElement('button'); item.type = 'button'; item.setAttribute('role', 'listitem');
              item.innerHTML = `<strong>${{String(index + 1).padStart(2, '0')}} · ${{event.status}}</strong>${{event.title}}`;
              item.addEventListener('click', () => {{ current = index; started = performance.now(); playing = false; toggle.textContent = 'Play'; render(0); }}); timeline.appendChild(item);
            }});
            document.getElementById('model-name').textContent = `model ${{sequence.model.model}} · ${{sequence.model.provider}}`;
            document.getElementById('source-name').textContent = `fixture ${{sequence.fixture}}`;
            function render(progress) {{
              const next = (current + 1) % points.length, from = points[current], to = points[next];
              const x = from[0] + (to[0] - from[0]) * progress, y = from[1] + (to[1] - from[1]) * progress;
              token.setAttribute('cx', x); token.setAttribute('cy', y); tokenLabel.setAttribute('x', x); tokenLabel.setAttribute('y', y + 4);
              title.textContent = events[current].title; detail.textContent = events[current].detail; metric.textContent = events[current].metric;
              document.querySelectorAll('.station').forEach((node, index) => {{ node.classList.toggle('active', index === current); node.classList.toggle('done', index < current); }});
              timeline.querySelectorAll('button').forEach((node, index) => node.setAttribute('aria-current', index === current ? 'step' : 'false'));
            }}
            function animate(now) {{ if (playing) {{ const progress = Math.min(1, (now - started) / duration); render(progress); if (progress >= 1) {{ current = (current + 1) % events.length; started = now; }} }} else {{ render(0); }} requestAnimationFrame(animate); }}
            toggle.addEventListener('click', () => {{ playing = !playing; started = performance.now(); toggle.textContent = playing ? 'Pause' : 'Play'; }});
            document.getElementById('replay').addEventListener('click', () => {{ current = 0; started = performance.now(); playing = true; toggle.textContent = 'Pause'; }});
            render(0); requestAnimationFrame(animate);
          </script>
        </body>
        </html>
        """
    )


def main() -> None:
    manifest = build_manifest()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    REEL.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REEL.write_text(reel_html(manifest), encoding="utf-8")
    print(f"wrote {MANIFEST.relative_to(ROOT)}")
    print(f"wrote {REEL.relative_to(ROOT)}")
    print(f"source checksum: {manifest['source']['sha256']}")
    print(f"vulnerable failures: {manifest['comparison']['vulnerable_mode']['failed_tests']}")
    print(f"safe failures: {manifest['comparison']['safe_mode']['failed_tests']}")


if __name__ == "__main__":
    main()
