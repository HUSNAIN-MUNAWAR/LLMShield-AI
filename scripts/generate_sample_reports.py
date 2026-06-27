from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/"backend"))
from app.services.report_writer import ReportWriter
from app.services.scanner import ScannerService
from app.services.target_clients import TargetConfig
def main():
    sample_log=ROOT/"sample_outputs"/"jsonl"/"sample_scan_report.jsonl"
    if sample_log.exists():
        sample_log.unlink()
    result=ScannerService().run_scan(TargetConfig(id="sample-mock",name="Sample MockLLM Unsafe",type="mock_llm",safe_mode=False), None, scan_id="sample_scan_report")
    out=ROOT/"sample_outputs"/"reports"; paths=ReportWriter(output_dir=out).write_all({"id":result.scan_id,"status":result.status,"risk_score":result.risk_score,"total_tests":result.total_tests,"passed_tests":result.passed_tests,"failed_tests":result.failed_tests,"target_id":"sample-mock"}, result.findings, "sample_scan_report")
    (ROOT/"sample_outputs"/"findings").mkdir(parents=True, exist_ok=True); (ROOT/"sample_outputs"/"findings"/"sample_findings.json").write_text(json.dumps(result.findings,indent=2, default=str),encoding="utf-8")
    print(json.dumps({"reports":paths,"tests":result.total_tests,"failed":result.failed_tests,"risk_score":result.risk_score},indent=2))
if __name__=="__main__": main()
