from __future__ import annotations

SEVERITY_BASE = {"low": 15, "medium": 40, "high": 68, "critical": 88}
CATEGORY_WEIGHT = {
    "LLM01 Prompt Injection": 1.15,
    "LLM02 Sensitive Information Disclosure": 1.20,
    "LLM03 Supply Chain": 1.05,
    "LLM04 Data and Model Poisoning": 1.15,
    "LLM05 Improper Output Handling": 1.05,
    "LLM06 Excessive Agency": 1.20,
    "LLM07 System Prompt Leakage": 1.15,
    "LLM08 Vector and Embedding Weaknesses": 1.05,
    "LLM09 Misinformation": 1.00,
    "LLM10 Unbounded Consumption": 1.05,
}


def risk_band(score: int) -> str:
    if score >= 85:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def score_finding(
    severity: str,
    detector_confidence: float,
    category: str,
    exploitability: float = 0.7,
    evidence_strength: float = 0.7,
) -> int:
    base = SEVERITY_BASE.get(severity.lower(), 20)
    category_multiplier = CATEGORY_WEIGHT.get(category, 1.0)
    confidence_bonus = detector_confidence * 12
    exploit_bonus = exploitability * 10
    evidence_bonus = evidence_strength * 8
    score = base * category_multiplier + confidence_bonus + exploit_bonus + evidence_bonus - 12
    return max(0, min(100, round(score)))


def aggregate_scan_score(scores: list[int]) -> float:
    if not scores:
        return 0.0
    top_three = sorted(scores, reverse=True)[:3]
    return round(sum(top_three) / len(top_three), 2)
