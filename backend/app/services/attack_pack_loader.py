from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, ConfigDict, Field
from app.core.config import settings
class AttackTest(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str; name: str; prompt: str; expected_safe_behavior: str; detector: dict[str, Any]; mitigation: str
    severity: str | None = None
    severity_default: str | None = None
    category: str | None = None
    references: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: str = "0.2.0"
    exploitability: float = 0.7
class AttackPack(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str; name: str; description: str; category: str; severity_default: str
    version: str = "0.2.0"
    attack_pack_version: str = "0.2.0"
    mitre_tactic: str = "Unmapped"
    tags: list[str] = Field(default_factory=list)
    tests: list[AttackTest]
class AttackPackLoader:
    def __init__(self, pack_dir: Path | None = None): self.pack_dir = pack_dir or settings.attack_pack_dir
    def load_all(self) -> list[AttackPack]: return [self.load_path(p) for p in sorted(self.pack_dir.glob("*.yaml"))]
    def load_path(self, path: Path) -> AttackPack: return AttackPack.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    def get_by_ids(self, ids: list[str] | None) -> list[AttackPack]:
        packs=self.load_all()
        return packs if not ids else [p for p in packs if p.id in set(ids)]
    def summaries(self) -> list[dict[str, Any]]:
        return [{"id":p.id,"name":p.name,"version":p.version,"attack_pack_version":p.attack_pack_version,"description":p.description,"category":p.category,"severity_default":p.severity_default,"mitre_tactic":p.mitre_tactic,"tags":p.tags,"test_count":len(p.tests)} for p in self.load_all()]
