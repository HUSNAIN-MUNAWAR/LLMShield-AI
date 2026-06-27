from app.services.report_writer import ReportWriter
from app.services.scanner import ScannerService
from app.services.target_clients import TargetConfig


def test_report_generation(tmp_path):
    result = ScannerService().run_scan(TargetConfig(id="mock", name="Mock", type="mock_llm"), ["prompt_injection"])
    writer = ReportWriter(output_dir=tmp_path)
    paths = writer.write_all({"id": result.scan_id, "status": result.status, "risk_score": result.risk_score, "total_tests": result.total_tests, "failed_tests": result.failed_tests, "passed_tests": result.passed_tests}, result.findings, result.scan_id)
    assert paths["json_path"].endswith(".json")
    assert paths["markdown_path"].endswith(".md")
    assert paths["html_path"].endswith(".html")
