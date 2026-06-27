from __future__ import annotations
from app.services.scan_executor import execute_scan
from app.services.scanner import ScannerService
from app.services.target_clients import TargetConfig

def execute_scan_job(scan_id: str):
    return execute_scan(scan_id)

def run_scan_job(scan_id: str, target: dict, attack_pack_ids: list[str]):
    # Backward-compatible task signature used by earlier tests.
    return ScannerService().run_scan(TargetConfig(**target), attack_pack_ids, scan_id=scan_id)
