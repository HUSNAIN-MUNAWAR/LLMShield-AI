from __future__ import annotations
import argparse, json
from pathlib import Path
from app.services.scanner import ScannerService
from app.services.target_clients import TargetConfig
ORDER={"low":1,"medium":2,"high":3,"critical":4}
def ci_scan(args):
    target=TargetConfig(id=args.target,name=args.target,type="mock_llm",safe_mode="safe" in args.target)
    packs=[p.strip() for p in args.attack_packs.split(",") if p.strip()]
    result=ScannerService().run_scan(target,packs)
    fail_level=ORDER[args.fail_on]
    threshold=[f for f in result.findings if not f["passed"] and ORDER.get(f["severity"],0)>=fail_level]
    payload={"scan_id":result.scan_id,"status":result.status,"risk_score":result.risk_score,"total_tests":result.total_tests,"failed_tests":result.failed_tests,"threshold_findings":len(threshold),"fail_on":args.fail_on}
    out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print("LLMShield CI Summary"); print(f"tests={result.total_tests} failed={result.failed_tests} risk={result.risk_score} threshold_findings={len(threshold)}")
    if args.max_risk_score is not None and result.risk_score > args.max_risk_score: return 1
    return 1 if threshold else 0
def main(argv=None):
    parser=argparse.ArgumentParser("llmshield"); sub=parser.add_subparsers(dest="command", required=True)
    ci=sub.add_parser("ci-scan"); ci.add_argument("--target",default="mock-safe"); ci.add_argument("--attack-packs",default="prompt_injection,jailbreak,rag_poisoning"); ci.add_argument("--fail-on",choices=["medium","high","critical"],default="high"); ci.add_argument("--output",default="sample_outputs/reports/ci_report.json"); ci.add_argument("--format",default="json"); ci.add_argument("--max-risk-score",type=float,default=None)
    args=parser.parse_args(argv)
    return ci_scan(args) if args.command=="ci-scan" else 2
if __name__=="__main__": raise SystemExit(main())
