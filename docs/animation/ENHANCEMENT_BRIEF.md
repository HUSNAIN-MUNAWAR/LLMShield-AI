# LLMShield security scan animation enhancement

## Purpose

Make the defensive loop visible: versioned attack packs send authorized prompts to a local deterministic model, detectors capture redacted evidence, risk is aggregated, and safe-mode behavior is compared.

## Model and service boundary

The generator executes the repository’s real path:

- `AttackPackLoader` loads the committed YAML packs.
- `ScannerService` runs the selected tests.
- `TargetClient` routes to `MockLLMClient` and `MockLLMProvider` without network access.
- `run_detector` selects the configured detector and keeps matched evidence.
- `redact_text` removes secrets and PII from report values.
- `aggregate_scan_score` produces the scan-level risk score.

The mock target and attack prompts are synthetic and defensive. The animation is not a real endpoint penetration test, security certification, or proof of general model behavior.

## Reproduce

```bash
python scripts/generate_security_animation.py
```

Outputs:

- `docs/animation/security_scan_sequence.json` — source checksum, provider/model references, stable findings, risk comparison, and scene events.
- `frontend/public/animation/security-scan-reel.html` — dependency-free animated reference reel with pause, replay, and stage selection.
