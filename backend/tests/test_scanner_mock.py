from app.services.scanner import ScannerService
from app.services.target_clients import TargetConfig


def test_mock_scanner_runs_and_produces_findings():
    target = TargetConfig(id="mock", name="Mock Unsafe", type="mock_llm", safe_mode=False)
    result = ScannerService().run_scan(target, ["prompt_injection", "sensitive_data_leakage"])
    assert result.status == "completed"
    assert result.total_tests == 8
    assert result.failed_tests >= 4
    assert result.risk_score > 50


def test_mock_safe_target_has_lower_risk():
    unsafe = ScannerService().run_scan(TargetConfig(id="u", name="u", type="mock_llm", safe_mode=False), ["prompt_injection"])
    safe = ScannerService().run_scan(TargetConfig(id="s", name="s", type="mock_llm", safe_mode=True), ["prompt_injection"])
    assert safe.risk_score < unsafe.risk_score
