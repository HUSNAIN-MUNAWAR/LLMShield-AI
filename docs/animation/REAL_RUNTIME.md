# LLMShield real scanner runtime evidence

This evidence is generated from the repository's real scanner and mock provider
execution, not from a decorative HTML storyboard.

## Reproduce

```powershell
py -3.12 -u scripts/generate_real_runtime_video.py
```

The runner loads the committed YAML attack packs, executes `ScannerService` on
the authorized synthetic target in vulnerable and safe modes, runs the detector
registry, redacts finding evidence, aggregates risk, and writes the actual
findings to CSV. Seven data-driven events are held for five frames each so the
execution trace is watchable.

## Model boundary

- provider: `backend/app/services/providers/mock_provider.py::MockLLMProvider`
- model: `mock-deterministic`
- learned checkpoint: none
- target: local synthetic target only
- external endpoint: false

The mock provider is deterministic rule-backed behavior. OpenAI and Ollama are
optional adapters and were not called in this run.

## Captured result

| Mode | Tests | Failed | Risk |
| --- | ---: | ---: | ---: |
| Vulnerable | 12 | 11 | 100.0 |
| Safe | 12 | 0 | 10.0 |

The CSV contains every finding/test result from both scans, including detector,
severity, risk, confidence, redacted response, evidence, and mitigation. The
JSON records the source hash, attack-pack counts, model boundary, runtime
versions, comparison, and output hashes.

This is synthetic defensive behavior evidence. It is not live LLM evaluation,
security certification, or a production accuracy claim.
