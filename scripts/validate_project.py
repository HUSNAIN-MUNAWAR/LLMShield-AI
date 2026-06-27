from __future__ import annotations
import ast, re, subprocess, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(cond,msg):
    if not cond: errors.append(msg)
required=['README.md','SECURITY.md','CONTRIBUTING.md','requirements-dev.txt','docker-compose.yml','Makefile','.env.example','backend/app/main.py','backend/app/api/routes_auth.py','backend/app/api/routes_api_keys.py','backend/app/core/redaction.py','backend/app/core/url_safety.py','backend/app/core/rate_limit.py','backend/app/services/providers/openai_provider.py','backend/app/services/providers/ollama_provider.py','backend/app/workers/queue.py','backend/app/services/scan_executor.py','backend/alembic.ini','backend/alembic/versions/0001_initial_professional_schema.py','frontend/package.json','frontend/package-lock.json','frontend/playwright.config.ts','frontend/tests/smoke.spec.ts','docs/deployment.md','docs/observability.md','docs/audit_logging.md','docs/security_boundaries.md','docs/production_hardening_checklist.md','docs/enterprise_auth_notes.md','scripts/secret_scan.py','scripts/provider_smoke_test.py','scripts/run_all_checks.py','scripts/docker_smoke_test.sh']
for item in required: check((ROOT/item).exists(), f"missing {item}")
readme=(ROOT/'README.md').read_text(encoding='utf-8')
check(readme.count('```mermaid')>=1,'README should contain an architecture diagram')
for section in ['## About','## Interface','## Quick start','## CI mode','## Validation','## Security boundaries']:
    check(section in readme, f'README missing {section}')
for phrase in ['authorized','API keys','Docker','Evidence']:
    check(phrase.lower() in readme.lower(), f'README missing {phrase}')
packs=list((ROOT/'backend/app/data/attack_packs').glob('*.yaml')); count=0
for path in packs:
    data=yaml.safe_load(path.read_text(encoding='utf-8')); check(data.get('attack_pack_version')=='0.2.0', f'{path.name} missing attack_pack_version 0.2.0'); count+=len(data.get('tests',[]))
check(count>=60, f'attack packs should have >=60 tests, got {count}')
for item in ['sample_scan_report.json','sample_scan_report.md','sample_scan_report.html','sample_scan_report.pdf']:
    check((ROOT/'sample_outputs/reports'/item).exists(), f'missing sample report {item}')
shots=['01-login.png','02-dashboard.png','03-targets.png','04-attack-packs.png','05-scans.png','06-findings.png','07-reports.png','08-settings-providers.png','09-audit-logs.png','10-docs.png']
for item in shots:
    check((ROOT/'sample_outputs/screenshots'/item).exists() or (ROOT/'frontend/public/screenshots'/item).exists(), f'missing screenshot {item}')
method=ROOT/'sample_outputs/screenshots/SCREENSHOT_METHOD.md'
check(method.exists(), 'missing screenshot method markdown')
if method.exists():
    check('Captured with Playwright Chromium from the running local app' in method.read_text(encoding='utf-8'), 'screenshots are not marked as real browser captures')
n=0
for path in (ROOT/'backend/tests').glob('test_*.py'):
    tree=ast.parse(path.read_text(encoding='utf-8')); n+=sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_') for node in tree.body)
check(n>=30, f'backend tests should have >=30 test functions, got {n}')
gitignore=(ROOT/'.gitignore').read_text(encoding='utf-8')
for pattern in ['.env','node_modules/','.next/','.venv/']:
    check(pattern in gitignore, f'.gitignore missing {pattern}')
if (ROOT/'.git').exists():
    tracked=subprocess.run(['git','ls-files'],cwd=ROOT,text=True,capture_output=True,check=False).stdout.splitlines()
    for forbidden in ['.env','frontend/.next/','frontend/node_modules/','.venv/']:
        is_tracked=any(item == forbidden if not forbidden.endswith('/') else item.startswith(forbidden) for item in tracked)
        check(not is_tracked, f'forbidden tracked artifact: {forbidden}')
lock=(ROOT/'frontend/package-lock.json').read_text(encoding='utf-8')
check('applied-caas-gateway' not in lock and 'internal.api.openai.org' not in lock, 'frontend lockfile references a private package registry')
secret=re.compile(r'sk-(?!demo)[A-Za-z0-9_\-]{20,}|AKIA[0-9A-Z]{12,}')
for path in [ROOT/'README.md', ROOT/'.env.example']:
    check(not secret.search(path.read_text(encoding='utf-8')), f'possible real secret in {path.name}')
if errors:
    print('Validation failed:'); [print('- '+e) for e in errors]; sys.exit(1)
print(f'Validation passed. attack_packs={len(packs)} tests={count} backend_test_functions={n}')
