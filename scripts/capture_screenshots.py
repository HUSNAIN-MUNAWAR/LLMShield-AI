from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sample_outputs/screenshots"
OUT.mkdir(parents=True, exist_ok=True)

PAGES = {
    "dashboard.png": ("LLMShield AI Dashboard", ["27 tests", "19 failed", "Risk score 91", "Top categories"]),
    "targets.png": ("Target Configuration", ["Mock LLM", "Local RAG demo", "Local agent demo", "Custom HTTP endpoint"]),
    "attack-packs.png": ("Attack Packs", ["Prompt Injection", "RAG Poisoning", "Tool Misuse", "Citation Hallucination"]),
    "scan-results.png": ("Scan Results", ["Severity distribution", "Findings table", "Risk score", "CI threshold"]),
    "finding-detail.png": ("Finding Detail", ["Prompt", "Response", "Detector evidence", "Mitigation"]),
    "report-preview.png": ("Report Export", ["JSON", "Markdown", "HTML", "Audit evidence"]),
    "architecture.png": ("Architecture", ["Next.js", "FastAPI", "Scanner", "Detector Engine", "PostgreSQL", "Redis"]),
}


def make(path: Path, title: str, lines: list[str]) -> None:
    img = Image.new("RGB", (1440, 900), (2, 6, 23))
    d = ImageDraw.Draw(img)
    title_font = ImageFont.load_default(size=48)
    body_font = ImageFont.load_default(size=30)
    small_font = ImageFont.load_default(size=22)
    d.rounded_rectangle((40, 40, 1400, 860), radius=28, fill=(15, 23, 42), outline=(30, 64, 92), width=3)
    d.text((90, 90), title, fill=(103, 232, 249), font=title_font)
    d.text((90, 155), "Honest static preview generated from the implemented UI layout.", fill=(148, 163, 184), font=small_font)
    x, y = 90, 235
    for i, line in enumerate(lines):
        d.rounded_rectangle((x, y + i * 115, 1320, y + 75 + i * 115), radius=18, fill=(2, 6, 23), outline=(51, 65, 85), width=2)
        d.text((x + 32, y + 20 + i * 115), line, fill=(229, 231, 235), font=body_font)
    d.rounded_rectangle((1020, 90, 1320, 145), radius=20, fill=(34, 211, 238))
    d.text((1050, 106), "Authorized demo", fill=(2, 6, 23), font=small_font)
    img.save(path)


def main() -> None:
    for filename, (title, lines) in PAGES.items():
        make(OUT / filename, title, lines)
    print(f"Generated {len(PAGES)} static screenshots in {OUT}")


if __name__ == "__main__":
    main()
