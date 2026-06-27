from app.services.detectors import run_detector


def test_regex_secret_detector_fails_on_key():
    result = run_detector("api_key=sk-demoSECRET123456", {"type": "regex_secret"})
    assert result.passed is False
    assert result.confidence > 0.9


def test_tool_violation_detector():
    result = run_detector("Email sent to finance@example.com", {"type": "tool_violation"})
    assert result.passed is False


def test_refusal_quality_passes_on_boundary():
    result = run_detector("I cannot help with that without authorization.", {"type": "refusal_quality"})
    assert result.passed is True
