from app.services.risk_scoring import aggregate_scan_score, risk_band, score_finding


def test_risk_score_bounds_and_band():
    score = score_finding("critical", 0.95, "LLM02 Sensitive Information Disclosure", 0.9, 0.9)
    assert 85 <= score <= 100
    assert risk_band(score) == "critical"


def test_aggregate_scan_score():
    assert aggregate_scan_score([10, 20, 90, 80]) == 63.33
