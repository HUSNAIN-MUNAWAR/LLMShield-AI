from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.database import SessionLocal, init_db
from app.models.target import Target


def main() -> None:
    init_db()
    seed = json.loads((ROOT / "backend/app/data/seed_targets.json").read_text(encoding="utf-8"))
    db = SessionLocal()
    try:
        for item in seed:
            exists = db.query(Target).filter(Target.name == item["name"]).first()
            if not exists:
                db.add(Target(name=item["name"], type=item["type"], safe_mode=item.get("safe_mode", False)))
        db.commit()
        print(f"Seeded {len(seed)} demo targets")
    finally:
        db.close()


if __name__ == "__main__":
    main()
