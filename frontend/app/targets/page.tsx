'use client';
import { useState } from 'react';
import { Card, PageHeader } from '../../components/ui';
import { demoTargets } from '../../lib/demo-data';
import { api } from '../../lib/api';
export default function TargetsPage() {
  const [message, setMessage] = useState('Custom endpoints are checked against allowlist and SSRF protections.');
  async function testTarget(id: string | number) { try { const r = await api.testTarget(id); setMessage(r.message); } catch { setMessage('Backend unavailable or target blocked by safety policy.'); } }
  return <div><PageHeader eyebrow="Scope control" title="Targets"><a className="btn" href="/scans">Create scan</a></PageHeader><Card className="mb-5 border-amber-400/20 bg-amber-400/10"><b>Endpoint safety warning:</b><p className="mt-2 text-sm text-amber-100">Only local demos, MockLLM, local providers, or explicitly allowlisted user-owned endpoints should be tested. Metadata IPs and unsafe private ranges are blocked unless demo mode permits them.</p></Card><div className="grid gap-4 lg:grid-cols-3">{demoTargets.map(t => <Card key={t.id}><h2 className="text-lg font-black text-white">{t.name}</h2><p className="mt-2 text-sm text-slate-400">Type: {t.type}</p><p className="mt-1 text-xs text-slate-500">{t.url || 'Provider-backed local target'}</p><button className="btn btn-secondary mt-5" onClick={() => testTarget(t.id)}>Test connection</button></Card>)}</div><p className="mt-4 text-sm text-sky-200">{message}</p></div>;
}
