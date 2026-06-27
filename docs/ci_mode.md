# CI Mode

Run:

```bash
cd backend
python -m app.services.ci_runner --target mock-unsafe --attack-packs prompt_injection,jailbreak,rag_poisoning --fail-on high --output ../sample_outputs/reports/ci_report.json
```

The command exits non-zero when the worst finding is at or above the configured threshold.
