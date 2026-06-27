#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, json, os, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'backend'))
from app.services.providers.base import ProviderOptions
from app.services.providers.mock_provider import MockLLMProvider
from app.services.providers.ollama_provider import OllamaProvider
from app.services.providers.openai_provider import OpenAIProvider

async def run(args):
    evidence=ROOT/'evidence'; evidence.mkdir(exist_ok=True)
    start=time.perf_counter()
    result={"provider":args.provider,"strict":args.strict,"dry_run":args.dry_run,"status":"unknown","latency_ms":0,"error":None}
    try:
        if args.provider=='mock':
            provider=MockLLMProvider(safe_mode=True)
            response=await provider.generate([{"role":"user","content":"Say one safe sentence for a smoke test."}], ProviderOptions(safe_mode=True))
            assert response.text
            result.update({"status":"passed","configured":True,"model":response.model,"response_preview":response.text[:120],"latency_ms":response.latency_ms})
        elif args.provider=='ollama':
            provider=OllamaProvider(model=args.model)
            health=await provider.health()
            result["health"]=health
            if not health.get('healthy'):
                result.update({"status":"skipped" if not args.strict else "failed","error":"Ollama is not reachable"})
            elif args.dry_run:
                result.update({"status":"passed","message":"Ollama health passed; dry-run skipped generation."})
            else:
                response=await provider.generate([{"role":"user","content":"Return one short safe sentence."}], ProviderOptions(model=args.model, timeout_seconds=args.timeout, max_output_tokens=32))
                result.update({"status":"passed" if not response.error else "failed","model":response.model,"latency_ms":response.latency_ms,"error":response.error,"response_preview":response.text[:120]})
        elif args.provider=='openai':
            configured=bool(os.getenv('OPENAI_API_KEY'))
            result['configured']=configured
            if args.dry_run:
                result.update({"status":"passed","message":"Dry-run only; no OpenAI request made."})
            elif not configured:
                result.update({"status":"skipped" if not args.strict else "failed","error":"OPENAI_API_KEY is not configured"})
            else:
                provider=OpenAIProvider(model=args.model)
                response=await provider.generate([{"role":"user","content":"Return one short safe sentence for a smoke test."}], ProviderOptions(model=args.model, timeout_seconds=args.timeout, max_output_tokens=24))
                result.update({"status":"passed" if not response.error else "failed","model":response.model,"latency_ms":response.latency_ms,"error":response.error,"response_preview":response.text[:120],"input_tokens_estimate":response.input_tokens_estimate,"output_tokens_estimate":response.output_tokens_estimate})
        else:
            result.update({"status":"failed","error":"Unsupported provider"})
    except Exception as exc:
        result.update({"status":"failed","error":str(exc)[:300]})
    result['elapsed_ms']=int((time.perf_counter()-start)*1000)
    out=evidence/f"provider_smoke_{args.provider}_result.txt"
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    # stable legacy name requested by user
    if args.provider=='mock': (evidence/'provider_smoke_mock_result.txt').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    if result['status']=='failed': return 1
    return 0

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--provider', choices=['mock','ollama','openai'], default='mock')
    parser.add_argument('--model', default=None)
    parser.add_argument('--timeout', type=float, default=15.0)
    parser.add_argument('--strict', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args=parser.parse_args()
    raise SystemExit(asyncio.run(run(args)))
if __name__=='__main__': main()
