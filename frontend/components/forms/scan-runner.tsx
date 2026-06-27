'use client';

import { useState } from 'react';
import { api } from '../../lib/api';
import type { AttackPack, Scan, Target } from '../../lib/types';

export function ScanRunner() {
  const [targets, setTargets] = useState<Target[]>([]);
  const [packs, setPacks] = useState<AttackPack[]>([]);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [selectedPacks, setSelectedPacks] = useState<string[]>(['prompt_injection', 'sensitive_data_leakage', 'tool_misuse']);
  const [scan, setScan] = useState<Scan | null>(null);
  const [status, setStatus] = useState('Load targets and packs from the backend, then run a scan.');

  async function loadConfig() {
    const [t, p] = await Promise.all([api.targets(), api.attackPacks()]);
    setTargets(t);
    setPacks(p);
    setSelectedTarget(t[0]?.id || '');
    setStatus(`Loaded ${t.length} targets and ${p.length} attack packs.`);
  }

  async function createAndRun() {
    if (!selectedTarget) {
      setStatus('Select or create a target first.');
      return;
    }
    setStatus('Creating scan...');
    const created = await api.createScan({ target_id: selectedTarget, attack_pack_ids: selectedPacks });
    setStatus('Running scan...');
    const completed = await api.runScan(created.id);
    setScan(completed);
    setStatus(`Scan completed with risk score ${completed.risk_score}.`);
  }

  function togglePack(id: string) {
    setSelectedPacks((current) => current.includes(id) ? current.filter((x) => x !== id) : [...current, id]);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="card lg:col-span-1">
        <h2 className="text-xl font-bold">Configure scan</h2>
        <button className="button-secondary mt-4" onClick={loadConfig}>Load targets & packs</button>
        <select className="input mt-4" value={selectedTarget} onChange={(e) => setSelectedTarget(e.target.value)}>
          <option value="">Select target</option>
          {targets.map((target) => <option key={target.id} value={target.id}>{target.name}</option>)}
        </select>
        <div className="mt-4 space-y-2 text-sm text-slate-300">
          {packs.slice(0, 9).map((pack) => <label key={pack.id} className="flex gap-2"><input type="checkbox" checked={selectedPacks.includes(pack.id)} onChange={() => togglePack(pack.id)} /> {pack.name}</label>)}
        </div>
        <button className="button mt-5" onClick={createAndRun}>Run scan via /api/scans/:id/run</button>
        <p className="mt-4 text-sm text-cyan-200">{status}</p>
      </div>
      <div className="card lg:col-span-2">
        <h2 className="text-xl font-bold">Scan Results</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-4">
          <div className="rounded-xl bg-slate-950 p-4"><div className="text-2xl font-bold">{scan?.total_tests ?? '—'}</div><div className="text-xs text-slate-500">Tests</div></div>
          <div className="rounded-xl bg-slate-950 p-4"><div className="text-2xl font-bold">{scan?.passed_tests ?? '—'}</div><div className="text-xs text-slate-500">Passed</div></div>
          <div className="rounded-xl bg-slate-950 p-4"><div className="text-2xl font-bold">{scan?.failed_tests ?? '—'}</div><div className="text-xs text-slate-500">Failed</div></div>
          <div className="rounded-xl bg-slate-950 p-4"><div className="text-2xl font-bold">{scan?.risk_score ?? '—'}</div><div className="text-xs text-slate-500">Risk</div></div>
        </div>
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-4 text-slate-400">Live results are returned from backend scan endpoints. Use the Findings page or /api/scans/:id/findings for details.</div>
      </div>
    </div>
  );
}
