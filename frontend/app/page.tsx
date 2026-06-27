import { Card, PageHeader, ProgressBar, SeverityBadge, Stat } from '../components/ui';
import { demoFindings, demoScans } from '../lib/demo-data';

export default function DashboardPage() {
  const critical = demoFindings.filter(f => f.severity === 'critical').length;
  return <div><PageHeader eyebrow="Risk Command Center" title="LLMShield AI"><a className="btn" href="/scans">Run demo scan</a></PageHeader>
    <div className="grid gap-4 md:grid-cols-4"><Stat label="Scans" value="3" hint="Seeded local demo runs" /><Stat label="Attack cases" value="60+" hint="Safe defensive prompts" /><Stat label="Critical findings" value={String(critical)} hint="Across local demo data" /><Stat label="Provider" value="MockLLM" hint="No paid key required" /></div>
    <div className="mt-6 grid gap-6 xl:grid-cols-3"><Card className="xl:col-span-2"><h2 className="text-xl font-black">Recent scan timeline</h2><div className="mt-5 space-y-5">{demoScans.map(s => <div key={s.id}><div className="mb-2 flex justify-between text-sm"><span className="font-bold text-slate-200">{s.name}</span><span className="text-slate-400">{s.status} · {s.progress}%</span></div><ProgressBar value={s.progress || 0}/></div>)}</div></Card><Card><h2 className="text-xl font-black">Top risky categories</h2><div className="mt-4 space-y-3">{demoFindings.map(f => <div key={f.id} className="rounded-xl bg-slate-900/70 p-3"><div className="flex items-center justify-between"><b>{f.category}</b><SeverityBadge value={f.severity}/></div><p className="mt-2 text-sm text-slate-400">Risk score {f.risk_score}</p></div>)}</div></Card></div>
    <Card className="mt-6"><h2 className="text-xl font-black">Security boundary</h2><p className="mt-2 text-slate-400">This dashboard is designed for authorized testing of local demo apps, MockLLM, local providers, or explicitly configured user-owned endpoints. It does not perform public-target scanning or real exploit deployment.</p></Card>
  </div>;
}
