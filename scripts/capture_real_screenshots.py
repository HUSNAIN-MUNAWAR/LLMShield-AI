#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'sample_outputs'/'screenshots'
PUB=ROOT/'frontend'/'public'/'screenshots'
EVIDENCE=ROOT/'evidence'; EVIDENCE.mkdir(exist_ok=True)
NAMES=[
 ('01-login.png','Login','Demo JWT/RBAC sign-in with admin, analyst, viewer roles.'),
 ('02-dashboard.png','Risk Command Center','Top risk cards, scan timeline, and current MockLLM demo status.'),
 ('03-targets.png','Targets','Endpoint allowlist warning and local/user-owned target configuration.'),
 ('04-attack-packs.png','Attack Packs','15 categories and 60 safe defensive test cases.'),
 ('05-scans.png','Scans','Target and attack-pack selection with bounded scan progress visibility.'),
 ('06-findings.png','Findings','Detector evidence, severity, risk score, and mitigation details.'),
 ('07-reports.png','Reports','JSON, Markdown, HTML, and real ReportLab PDF export.'),
 ('08-settings-providers.png','Provider Settings','MockLLM, OpenAI, and Ollama health without exposing secrets.'),
 ('09-audit-logs.png','Audit Logs','Login, target creation, scan start, report export, and failed validation audit events.'),
 ('10-docs.png','Docs','Authorized testing boundary, limitations, and deployment guidance.'),
]
URLS={
 '01-login.png':'/login','02-dashboard.png':'/','03-targets.png':'/targets','04-attack-packs.png':'/attack-packs',
 '05-scans.png':'/scans','06-findings.png':'/findings','07-reports.png':'/reports',
 '08-settings-providers.png':'/settings','09-audit-logs.png':'/audit-logs','10-docs.png':'/docs'
}

def clear_pngs(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    for path in directory.glob('*.png'):
        path.unlink()

def copy_all():
    PUB.mkdir(parents=True, exist_ok=True)
    for path in OUT.glob('*.png'):
        shutil.copy2(path, PUB/path.name)
    for name in ['SCREENSHOT_METHOD.md','SCREENSHOT_METHOD.txt']:
        if (OUT/name).exists(): shutil.copy2(OUT/name, PUB/name)

def draw_fallback(reason: str):
    clear_pngs(OUT); clear_pngs(PUB)
    try: font_title=ImageFont.truetype('DejaVuSans-Bold.ttf', 38); font=ImageFont.truetype('DejaVuSans.ttf', 18); small=ImageFont.truetype('DejaVuSans.ttf', 14)
    except Exception: font_title=font=small=None
    for idx,(name,title,desc) in enumerate(NAMES,1):
        img=Image.new('RGB',(1440,900),(7,13,28)); d=ImageDraw.Draw(img)
        # Sidebar and header
        d.rectangle([0,0,260,900], fill=(11,18,35)); d.rectangle([260,0,1440,88], fill=(10,20,42))
        d.text((34,32),'LLMShield AI', fill=(226,232,240), font=font_title)
        nav=['Dashboard','Targets','Attack Packs','Scans','Findings','Reports','Settings','Audit Logs','Docs']
        y=120
        for item in nav:
            active = item.lower().replace(' ','-') in title.lower().replace(' ','-') or (title=='Risk Command Center' and item=='Dashboard')
            color=(14,165,233) if active else (100,116,139)
            d.rounded_rectangle([24,y,236,y+42], radius=12, fill=(15,23,42) if active else (11,18,35))
            d.text((44,y+12),item,fill=color,font=font); y+=55
        d.text((305,28),title,fill=(248,250,252),font=font_title)
        d.text((306,70),'Static fallback preview generated from implemented UI layout',fill=(148,163,184),font=small)
        # Cards
        x0=305; y0=130
        for c in range(4):
            x=x0+c*265
            d.rounded_rectangle([x,y0,x+240,y0+130], radius=22, fill=(15,23,42), outline=(30,41,59))
            d.text((x+22,y0+22),['Scans','Attack cases','Critical','Provider'][c],fill=(148,163,184),font=font)
            d.text((x+22,y0+62),['3','60+','1','MockLLM'][c],fill=(248,250,252),font=font_title)
        # Main panel
        d.rounded_rectangle([305,300,1375,805], radius=24, fill=(15,23,42), outline=(30,41,59))
        d.text((340,330),title,fill=(226,232,240),font=font_title)
        d.text((340,385),desc,fill=(203,213,225),font=font)
        # table lines
        for r in range(6):
            y=455+r*48
            d.rounded_rectangle([340,y,1338,y+32],radius=8,fill=(2+r*3,8+r*3,23+r*3))
            d.text((360,y+8),f'Demo row {r+1}: redacted evidence, severity, mitigation, and audit metadata', fill=(148,163,184), font=small)
        d.rounded_rectangle([340,735,610,775], radius=14, fill=(14,165,233))
        d.text((365,746),'Authorized local demo only',fill=(255,255,255),font=font)
        d.text((1160,840),f'{idx:02d}/{len(NAMES):02d}', fill=(100,116,139), font=font)
        img.save(OUT/name)
    method=f"""# Screenshot method\n\nStatic fallback previews generated because browser automation was unavailable.\n\nGenerated at: {datetime.now(timezone.utc).isoformat()}\n\nReason: {reason}\n\nTo capture real browser screenshots locally:\n\n```bash\ncd frontend && npm install\ncd ..\npython scripts/capture_real_screenshots.py --real\npython scripts/verify_screenshots.py\n```\n\nReal screenshots should only be described as browser-captured after Playwright successfully navigates the running Next.js app and writes this file with a Playwright success message.\n"""
    (OUT/'SCREENSHOT_METHOD.md').write_text(method, encoding='utf-8')
    (OUT/'SCREENSHOT_METHOD.txt').write_text(method, encoding='utf-8')
    copy_all()
    (EVIDENCE/'screenshot_result.txt').write_text('STATIC FALLBACK: '+reason+'\n', encoding='utf-8')

def wait_url(url: str, seconds: int = 45) -> bool:
    import urllib.request
    end=time.time()+seconds
    while time.time()<end:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status < 500: return True
        except Exception:
            time.sleep(1)
    return False

def start_processes(install: bool=False):
    procs=[]
    backend=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000'], cwd=ROOT/'backend', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(backend)
    npm=shutil.which('npm.cmd' if sys.platform == 'win32' else 'npm')
    if not npm:
        raise RuntimeError('npm was not found on PATH')
    if install and not (ROOT/'frontend'/'node_modules').exists():
        subprocess.run([npm,'install'], cwd=ROOT/'frontend', check=False)
    if not (ROOT/'frontend'/'node_modules').exists():
        raise RuntimeError('frontend/node_modules is missing; run npm install or use static fallback')
    frontend=subprocess.Popen([npm,'run','dev','--','-H','127.0.0.1','-p','3000'], cwd=ROOT/'frontend', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(frontend)
    if not wait_url('http://127.0.0.1:8000/health',45): raise RuntimeError('backend health did not become ready')
    if not wait_url('http://127.0.0.1:3000',90): raise RuntimeError('frontend did not become ready')
    return procs

def stop_processes(procs: Iterable[subprocess.Popen]):
    for proc in reversed(list(procs)):
        if sys.platform == 'win32' and proc.poll() is None:
            subprocess.run(
                ['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        elif proc.poll() is None:
            proc.terminate()
    for proc in procs:
        try: proc.wait(timeout=8)
        except Exception:
            if proc.poll() is None: proc.kill()

def real_capture(install: bool=False):
    procs=[]
    try:
        procs=start_processes(install=install)
        from playwright.sync_api import sync_playwright
        with tempfile.TemporaryDirectory(prefix='llmshield-screenshots-') as tmp:
            staged=Path(tmp)
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True, args=['--disable-gpu'])
                for name,_,_ in NAMES:
                    page=browser.new_page(viewport={'width':1440,'height':900})
                    page.goto('http://127.0.0.1:3000'+URLS[name], wait_until='networkidle', timeout=30000)
                    page.wait_for_timeout(250)
                    page.screenshot(path=str(staged/name), full_page=False)
                    page.close()
                browser.close()
            clear_pngs(OUT); clear_pngs(PUB)
            for path in staged.glob('*.png'):
                shutil.copy2(path, OUT/path.name)
        method=f"# Screenshot method\n\nCaptured with Playwright Chromium from the running local app on {datetime.now(timezone.utc).isoformat()}.\n\nBackend: http://127.0.0.1:8000\nFrontend: http://127.0.0.1:3000\n"
        (OUT/'SCREENSHOT_METHOD.md').write_text(method,encoding='utf-8'); (OUT/'SCREENSHOT_METHOD.txt').write_text(method,encoding='utf-8')
        copy_all(); (EVIDENCE/'screenshot_result.txt').write_text('PASSED: real Playwright browser screenshots captured.\n',encoding='utf-8')
        return True
    finally:
        stop_processes(procs)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--real',action='store_true'); ap.add_argument('--install',action='store_true')
    args=ap.parse_args()
    if args.real:
        try:
            real_capture(install=args.install); return 0
        except Exception as exc:
            print(f'Playwright capture failed; existing screenshots were preserved: {exc}'); return 2
    print('No screenshots were changed. Pass --real to capture the running application.')
    return 0
if __name__=='__main__': raise SystemExit(main())
