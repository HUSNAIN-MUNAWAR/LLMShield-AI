# LLMShield security scan reel storyboard

| Scene | Visual cue | Evidence shown | Gate |
| --- | --- | --- | --- |
| 01 · packs | Attack-pack cards load | Pack IDs, versions, test count | Only selected authorized test cases run |
| 02 · provider | Prompts enter MockLLM | Provider/model, safe-mode switch | No external endpoint or key |
| 03 · detect | Response passes detector nodes | Detector name, matched evidence | Redaction applies before evidence storage |
| 04 · findings | Failed cases turn red | Severity, confidence, category, mitigation | Finding is auditable |
| 05 · risk | Risk gauge aggregates | Top-three score logic and distribution | Scan-level decision is explainable |
| 06 · safe mode | Same suite replays green | Vulnerable vs safe failure/risk comparison | Control effect is measurable in the demo |
| 07 · report | Evidence packet closes | JSON/Markdown/HTML/PDF-ready outputs | Defensive reporting only |

Exact generated values are stored in `security_scan_sequence.json`.
