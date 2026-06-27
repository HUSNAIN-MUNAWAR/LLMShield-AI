#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'evidence'; EVIDENCE.mkdir(exist_ok=True)

def run(name: str, cmd: list[str], cwd: Path | None=None, allow_fail: bool=False, env: dict | None=None, timeout_seconds: int = 180) -> tuple[int,str]:
    merged=os.environ.copy()
    if env: merged.update(env)
    try:
        proc=subprocess.run(cmd,cwd=cwd or ROOT,text=True,capture_output=True,env=merged,timeout=timeout_seconds)
        code=proc.returncode; stdout=proc.stdout; stderr=proc.stderr
    except subprocess.TimeoutExpired as exc:
        code=124; stdout=(exc.stdout or '') if isinstance(exc.stdout, str) else ''; stderr=(exc.stderr or '') if isinstance(exc.stderr, str) else ''
        stderr += f'\nTIMEOUT: command exceeded {timeout_seconds} seconds.\n'
    def portable(value: str) -> str:
        return (
            value
            .replace(str(ROOT), '.')
            .replace(str(ROOT).replace('\\','/'), '.')
            .replace(str(ROOT).replace('\\','\\\\'), '.')
            .replace('.\\.venv', '<venv>')
            .replace('./.venv', '<venv>')
        )
    def clean(value: str) -> str:
        return '\n'.join(line.rstrip() for line in portable(value).splitlines()).strip()
    shown_cmd=list(cmd)
    try:
        if Path(shown_cmd[0]).resolve() == Path(sys.executable).resolve():
            shown_cmd[0]='python'
    except Exception:
        pass
    shown_cwd='.' if cwd is None else portable(str(cwd))
    shown_stdout=clean(stdout) or '(none)'
    shown_stderr=clean(stderr) or '(none)'
    text=f"$ {' '.join(portable(part) for part in shown_cmd)}\ncwd={shown_cwd}\nexit_code={code}\n\nSTDOUT:\n{shown_stdout}\n\nSTDERR:\n{shown_stderr}\n"
    (EVIDENCE/f'{name}.txt').write_text(text, encoding='utf-8')
    print(f'{name}: exit {code}')
    if code and not allow_fail:
        print(text[-4000:])
    return code, text

def main():
    results={"generated_at":datetime.now(timezone.utc).isoformat(),"checks":{}}
    checks=[
        ('backend_compile',[sys.executable,'-m','compileall','-q','backend/app','backend/tests'],None,False),
        ('validation_result',[sys.executable,'scripts/validate_project.py'],None,False),
        ('secret_scan_result',[sys.executable,'scripts/secret_scan.py'],None,False),
        ('backend_tests_result',[sys.executable,'-m','pytest','-q'],ROOT/'backend',False),
        ('sample_reports_result',[sys.executable,'scripts/generate_sample_reports.py'],None,False),
        ('provider_smoke_mock_result',[sys.executable,'scripts/provider_smoke_test.py','--provider','mock'],None,False),
        ('screenshot_verify_result',[sys.executable,'scripts/verify_screenshots.py'],None,False),
        ('docker_smoke_result',[sys.executable,'scripts/check_docker_compose.py'],None,True),
    ]
    if os.getenv('CAPTURE_SCREENSHOTS') == '1':
        checks.insert(
            -2,
            ('screenshot_capture_result',[sys.executable,'scripts/capture_real_screenshots.py','--real'],None,True),
        )
    for name,cmd,cwd,allow_fail in checks:
        code,_=run(name,cmd,cwd,allow_fail)
        results['checks'][name]={'exit_code':code,'required':not allow_fail}
    # Frontend checks are run only when node_modules already exists; the script does not install dependencies automatically
    # because CI/local machines should use npm ci/npm install explicitly and some restricted environments may hang.
    if (ROOT/'frontend'/'node_modules').exists():
        npm=shutil.which('npm.cmd' if sys.platform == 'win32' else 'npm') or 'npm'
        code,_=run('frontend_typecheck_result',[npm,'run','typecheck'],ROOT/'frontend',False)
        results['checks']['frontend_typecheck_result']={'exit_code':code,'required':True}
        if os.getenv('RUN_FRONTEND_BUILD') == '1':
            code,_=run('frontend_build_result',[npm,'run','build'],ROOT/'frontend',False)
            results['checks']['frontend_build_result']={'exit_code':code,'required':True}
        else:
            msg='NOT RUN by run_all_checks default: set RUN_FRONTEND_BUILD=1 to attempt Next.js production build. Run npm install first.\n'
            (EVIDENCE/'frontend_build_result.txt').write_text(msg,encoding='utf-8')
            results['checks']['frontend_build_result']={'exit_code':2,'required':False}
    else:
        msg='NOT RUN: frontend/node_modules is not present. Run cd frontend && npm install, then npm run typecheck and npm run build locally.\n'
        if not (EVIDENCE/'frontend_typecheck_result.txt').exists():
            (EVIDENCE/'frontend_typecheck_result.txt').write_text(msg,encoding='utf-8')
        if not (EVIDENCE/'frontend_build_result.txt').exists():
            (EVIDENCE/'frontend_build_result.txt').write_text(msg,encoding='utf-8')
        results['checks']['frontend_typecheck_result']={'exit_code':2,'required':False}
        results['checks']['frontend_build_result']={'exit_code':2,'required':False}
    # PDF render evidence: verify PDF exists and magic bytes.
    pdf=ROOT/'sample_outputs'/'reports'/'sample_scan_report.pdf'
    if pdf.exists() and pdf.read_bytes()[:4]==b'%PDF':
        msg=f'PASSED: PDF exists and starts with %PDF. size_bytes={pdf.stat().st_size}\n'
        code=0
    else:
        msg='FAILED: sample PDF missing or invalid.\n'; code=1
    (EVIDENCE/'sample_pdf_render_result.txt').write_text(msg, encoding='utf-8')
    print('sample_pdf_render_result:', msg.strip())
    results['checks']['sample_pdf_render_result']={'exit_code':code,'required':True}
    required_failed=[k for k,v in results['checks'].items() if v.get('required') and v.get('exit_code')!=0]
    results['required_failed']=required_failed
    (EVIDENCE/'run_all_checks_summary.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    return 1 if required_failed else 0
if __name__=='__main__': raise SystemExit(main())
