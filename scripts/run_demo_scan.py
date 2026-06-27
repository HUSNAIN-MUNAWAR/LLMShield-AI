from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/"backend"))
from app.services.scanner import ScannerService
from app.services.target_clients import TargetConfig
if __name__=="__main__":
    result=ScannerService().run_scan(TargetConfig(id="demo",name="Demo MockLLM",type="mock_llm",safe_mode=False), ["prompt_injection","secret_leakage","tool_misuse"])
    print(json.dumps({"scan_id":result.scan_id,"tests":result.total_tests,"failed":result.failed_tests,"risk_score":result.risk_score},indent=2))
