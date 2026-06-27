# Screenshots

The images in `sample_outputs/screenshots` are captured from the running FastAPI and Next.js application with Playwright Chromium. The capture manifest records the method and timestamp in `sample_outputs/screenshots/SCREENSHOT_METHOD.md`.

Regenerate and verify the complete route gallery:

```bash
python scripts/capture_real_screenshots.py --real
python scripts/verify_screenshots.py
```
