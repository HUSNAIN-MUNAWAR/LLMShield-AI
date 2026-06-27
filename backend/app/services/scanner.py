from __future__ import annotations
import json, uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.core.config import settings
from app.core.redaction import redact_mapping, redact_text
from app.services.attack_pack_loader import AttackPackLoader
from app.services.detectors import run_detector
from app.services.risk_scoring import aggregate_scan_score, risk_band, score_finding
from app.services.scan_queue import is_cancelled, update_status
from app.services.target_clients import TargetClient, TargetConfig
@dataclass(frozen=True)
class ScanResult:
    scan_id: str; status: str; target: dict[str, Any]; total_tests: int; passed_tests: int; failed_tests: int; risk_score: float; findings: list[dict[str,Any]]; started_at: str; completed_at: str
class ScannerService:
    def __init__(self, loader: AttackPackLoader | None = None, target_client: TargetClient | None = None):
        self.loader=loader or AttackPackLoader(); self.target_client=target_client or TargetClient(); settings.scan_logs_dir.mkdir(parents=True, exist_ok=True)
    def run_scan(self, target: TargetConfig, attack_pack_ids: list[str] | None = None, scan_id: str | None = None) -> ScanResult:
        run_id=scan_id or str(uuid.uuid4()); started=datetime.now(timezone.utc); packs=self.loader.get_by_ids(attack_pack_ids); total=sum(len(p.tests) for p in packs); findings=[]; scores=[]; executed=0
        update_status(run_id,status="running",progress=0,started_at=started.isoformat())
        for pack in packs:
            for test in pack.tests:
                if is_cancelled(run_id): return self._build_result(run_id,"cancelled",target,findings,scores,started,datetime.now(timezone.utc))
                update_status(run_id,current_test=f"{pack.id}/{test.id}",progress=int((executed/max(1,total))*100))
                try:
                    response=self.target_client.send_prompt(target,test.prompt); response_text=response.text if not response.error else f"Provider error: {response.error}"; det=run_detector(response_text,test.detector)
                except Exception as exc:
                    response_text=f"Scan execution error: {redact_text(str(exc))}"; det=run_detector(response_text,{"type":"refusal_quality"})
                    response=type("Resp",(),{"latency_ms":0,"token_estimate":0,"provider":"error","model":"none"})()
                sev_seed=(test.severity or pack.severity_default).lower()
                if det.passed: risk=score_finding("low",0.15,pack.category,0.1,0.1); severity="low"
                else: risk=score_finding(sev_seed,det.confidence,pack.category,exploitability=test.exploitability,evidence_strength=min(1.0,0.45+det.confidence/2)); severity=risk_band(risk)
                finding={"id":str(uuid.uuid4()),"scan_id":run_id,"attack_pack_id":pack.id,"test_id":test.id,"test_name":test.name,"prompt":redact_text(test.prompt),"response":redact_text(response_text),"detector_name":det.detector_name,"passed":det.passed,"severity":severity,"risk_score":risk,"category":pack.category,"mitre_tactic":pack.mitre_tactic,"confidence":det.confidence,"evidence":redact_text(det.evidence),"mitigation":test.mitigation,"latency_ms":getattr(response,"latency_ms",0),"token_estimate":getattr(response,"token_estimate",0),"created_at":datetime.now(timezone.utc)}
                findings.append(finding); scores.append(risk); self._append_jsonl(run_id,finding); executed+=1; update_status(run_id,progress=int((executed/max(1,total))*100),current_test=f"{pack.id}/{test.id}")
        completed=datetime.now(timezone.utc); update_status(run_id,status="completed",progress=100,completed_at=completed.isoformat(),current_test=None)
        return self._build_result(run_id,"completed",target,findings,scores,started,completed)
    def _build_result(self, run_id, status, target, findings, scores, started, completed):
        failed=len([f for f in findings if not f["passed"]])
        return ScanResult(run_id,status,{"id":target.id,"name":target.name,"type":target.type,"safe_mode":target.safe_mode},len(findings),len(findings)-failed,failed,aggregate_scan_score(scores),findings,started.isoformat(),completed.isoformat())
    def _append_jsonl(self, scan_id, item):
        path=settings.scan_logs_dir/f"{scan_id}.jsonl"
        with path.open("a",encoding="utf-8") as f: f.write(json.dumps(redact_mapping(item), default=str)+"\n")
def severity_distribution(findings: list[dict[str,Any]]):
    d={"low":0,"medium":0,"high":0,"critical":0}
    for f in findings: d[f["severity"]]=d.get(f["severity"],0)+1
    return d
def category_distribution(findings: list[dict[str,Any]]):
    d={}
    for f in findings: d[f["category"]]=d.get(f["category"],0)+1
    return d
def write_scan_result(result: ScanResult, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(result.__dict__,indent=2),encoding="utf-8")
