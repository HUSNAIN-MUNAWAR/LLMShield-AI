from __future__ import annotations
import asyncio, os, subprocess, sys
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.core.redaction import redact_text
from app.core.url_safety import validate_target_url
from app.services.scan_queue import cancel_scan, is_cancelled
from app.workers.queue import enqueue_scan
from app.services.providers.mock_provider import MockLLMProvider
from app.services.providers.base import ProviderOptions

client = TestClient(app)

def _admin_token():
    r=client.post('/api/auth/demo-login?role=admin')
    assert r.status_code==200
    return r.json()['access_token']

def test_refresh_token_flow():
    r=client.post('/api/auth/demo-login?role=analyst')
    assert r.status_code==200
    refresh=r.json()['refresh_token']
    r2=client.post('/api/auth/refresh', json={'refresh_token':refresh})
    assert r2.status_code==200
    assert r2.json()['access_token']

def test_api_key_create_list_and_revoke():
    token=_admin_token()
    r=client.post('/api/api-keys', headers={'Authorization':f'Bearer {token}'}, json={'name':'CI test key','scoped_role':'ci_runner'})
    assert r.status_code==200
    data=r.json(); assert data['api_key'].startswith('lsk_')
    r2=client.get('/api/api-keys', headers={'Authorization':f'Bearer {token}'})
    assert r2.status_code==200 and any(k['id']==data['id'] for k in r2.json())
    r3=client.delete(f"/api/api-keys/{data['id']}", headers={'Authorization':f'Bearer {token}'})
    assert r3.status_code==200

def test_api_key_can_authenticate_me_endpoint():
    token=_admin_token()
    r=client.post('/api/api-keys', headers={'Authorization':f'Bearer {token}'}, json={'name':'Viewer key','scoped_role':'viewer'})
    key=r.json()['api_key']
    me=client.get('/api/auth/me', headers={'X-LLMShield-API-Key':key})
    assert me.status_code==200
    assert me.json()['role']=='viewer'

def test_endpoint_allowlist_blocks_metadata_ip():
    result=validate_target_url('http://169.254.169.254/latest/meta-data', allow_private=False)
    assert not result.allowed

def test_endpoint_allowlist_blocks_unlisted_host():
    result=validate_target_url('https://not-owned-example.invalid/api', allow_private=False)
    assert not result.allowed

def test_redaction_removes_bearer_and_keys():
    text='Authorization: ' + 'Bearer ' + 'abcdefghijklmnopqrstuvwxyz' + ' and api_key=' + 'sk-demoSECRET123456789012345'
    out=redact_text(text)
    assert 'Bearer abc' not in out
    assert 'sk-demoSECRET' not in out
    assert '[REDACTED' in out

def test_async_enqueue_graceful_without_redis():
    result=enqueue_scan('scan-test-123456789')
    assert result.job_id
    assert result.backend in {'rq','memory-fallback'}

def test_cancel_scan_state():
    cancel_scan('cancel-proof-test')
    assert is_cancelled('cancel-proof-test')

def test_mock_provider_smoke_direct():
    async def _run():
        provider=MockLLMProvider(safe_mode=True)
        return await provider.generate([{'role':'user','content':'safe smoke test'}], ProviderOptions())
    resp=asyncio.run(_run())
    assert resp.provider=='mock'
    assert resp.text

def test_provider_smoke_script_mock():
    root=Path(__file__).resolve().parents[2]
    proc=subprocess.run([sys.executable, 'scripts/provider_smoke_test.py', '--provider', 'mock'], cwd=root, text=True, capture_output=True)
    assert proc.returncode==0
    assert 'passed' in proc.stdout.lower()

def test_openai_smoke_dry_run_script():
    root=Path(__file__).resolve().parents[2]
    proc=subprocess.run([sys.executable, 'scripts/provider_smoke_test.py', '--provider', 'openai', '--dry-run'], cwd=root, text=True, capture_output=True)
    assert proc.returncode==0
    assert 'Dry-run' in proc.stdout or 'dry-run' in proc.stdout.lower()

def test_secret_scan_script_passes():
    root=Path(__file__).resolve().parents[2]
    proc=subprocess.run([sys.executable, 'scripts/secret_scan.py'], cwd=root, text=True, capture_output=True)
    assert proc.returncode==0, proc.stdout + proc.stderr
