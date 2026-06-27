'use client';

import { useState } from 'react';
import { api } from '../../lib/api';
import type { Target } from '../../lib/types';

export function TargetManager() {
  const [name, setName] = useState('Mock Unsafe LLM');
  const [type, setType] = useState('mock_llm');
  const [safeMode, setSafeMode] = useState(false);
  const [endpointUrl, setEndpointUrl] = useState('');
  const [targets, setTargets] = useState<Target[]>([]);
  const [status, setStatus] = useState('Ready. Buttons call real backend endpoints when the API is running.');

  async function refresh() {
    setTargets(await api.targets());
  }

  async function createTarget() {
    setStatus('Creating target...');
    await api.createTarget({ name, type, endpoint_url: endpointUrl || null, safe_mode: safeMode });
    await refresh();
    setStatus('Target created through POST /api/targets.');
  }

  async function testConnection() {
    const health = await api.health();
    setStatus(`Backend health: ${health.status}`);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="card space-y-4">
        <h2 className="text-xl font-bold">Create target</h2>
        <input className="input" value={name} onChange={(e) => setName(e.target.value)} />
        <select className="input" value={type} onChange={(e) => setType(e.target.value)}>
          <option value="mock_llm">Mock LLM</option>
          <option value="local_vulnerable_chatbot">Local vulnerable chatbot</option>
          <option value="local_rag_demo">Local RAG demo</option>
          <option value="local_agent_demo">Local agent demo</option>
          <option value="custom_http">Custom HTTP endpoint</option>
        </select>
        <input className="input" value={endpointUrl} onChange={(e) => setEndpointUrl(e.target.value)} placeholder="Optional endpoint URL" />
        <label className="flex items-center gap-3 text-sm text-slate-300"><input type="checkbox" checked={safeMode} onChange={(e) => setSafeMode(e.target.checked)} /> Safe mode mitigation</label>
        <div className="flex gap-3">
          <button className="button" type="button" onClick={createTarget}>Create via /api/targets</button>
          <button className="button-secondary" type="button" onClick={testConnection}>Test backend</button>
        </div>
        <p className="text-sm text-cyan-200">{status}</p>
      </div>
      <div className="card">
        <div className="flex items-center justify-between"><h2 className="text-xl font-bold">Targets from API</h2><button className="button-secondary" onClick={refresh}>Refresh</button></div>
        <div className="mt-4 space-y-3">
          {targets.map((target) => (
            <div key={target.id} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <div className="font-semibold">{target.name}</div><div className="text-sm text-slate-500">{target.type} · safe mode: {String(target.safe_mode)}</div>
            </div>
          ))}
          {targets.length === 0 && <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm text-slate-500">No API targets loaded yet. Click Refresh or create one.</div>}
        </div>
      </div>
    </div>
  );
}
