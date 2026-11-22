# Animation assets

`security-scan-reel.html` is generated from the repository’s actual scanner and deterministic MockLLM path using the committed synthetic scan fixture.

Regenerate after changing attack packs, provider behavior, detectors, redaction, or risk scoring:

```bash
python scripts/generate_security_animation.py
```
