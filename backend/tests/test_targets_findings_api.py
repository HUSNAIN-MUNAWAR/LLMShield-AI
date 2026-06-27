from fastapi.testclient import TestClient

from app.main import app
from app.core.database import init_db


def test_target_scan_findings_flow():
    init_db()
    client = TestClient(app)
    target_resp = client.post("/api/targets", json={"name": "Pytest Mock", "type": "mock_llm", "safe_mode": False})
    assert target_resp.status_code == 200
    target_id = target_resp.json()["id"]
    scan_resp = client.post("/api/scans", json={"target_id": target_id, "attack_pack_ids": ["prompt_injection"]})
    assert scan_resp.status_code == 200
    scan_id = scan_resp.json()["id"]
    run_resp = client.post(f"/api/scans/{scan_id}/run")
    assert run_resp.status_code == 200
    status_resp = client.get(f"/api/scans/{scan_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["progress"] == 100
    findings_resp = client.get(f"/api/scans/{scan_id}/findings")
    assert findings_resp.status_code == 200
    assert len(findings_resp.json()) == 4
