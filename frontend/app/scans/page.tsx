'use client';
import { useEffect, useState } from 'react';
import { Card, PageHeader, ProgressBar, SeverityBadge } from '../../components/ui';
import { demoFindings, demoScans } from '../../lib/demo-data';
export default function ScansPage() {
  const [progress, setProgress] = useState(64);
  useEffect(() => { const id = setInterval(() => setProgress(p => Math.min(100, p + 3)), 1200); return () => clearInterval(id); }, []);
  return <div><PageHeader eyebrow="Queue and worker visibility" title="Scans"><button className="btn">Run MockLLM scan</button></PageHeader><div className="grid gap-5 lg:grid-cols-3"><Card className="lg:col-span-2"><h2 className="text-xl font-black">Live scan progress</h2><p className="mt-2 text-slate-400">Polling endpoint: GET /api/scans/{'{scan_id}'}/status</p><div className="mt-6"><div className="mb-2 flex justify-between text-sm"><span>Current test: indirect_prompt_injection_003</span><span>{progress}%</span></div><ProgressBar value={progress}/></div><div className="mt-6 overflow-hidden rounded-xl border border-slate-800"><table className="table"><thead><tr><th>Name</th><th>Status</th><th>Risk</th></tr></thead><tbody>{demoScans.map(s => <tr key={s.id}><td>{s.name}</td><td>{s.status}</td><td>{s.risk_score}</td></tr>)}</tbody></table></div></Card><Card><h2 className="text-xl font-black">Partial findings</h2><div className="mt-4 space-y-3">{demoFindings.map(f => <div key={f.id} className="rounded-xl bg-slate-900/80 p-3"><div className="flex justify-between"><b>{f.category}</b><SeverityBadge value={f.severity}/></div></div>)}</div></Card></div></div>;
}
