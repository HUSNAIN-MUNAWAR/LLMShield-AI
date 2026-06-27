'use client';
import { useState } from 'react';
import { api } from '../../lib/api';
import { Card, PageHeader } from '../../components/ui';
export default function LoginPage() {
  const [status, setStatus] = useState('Not signed in');
  async function demo(role: string) { try { const r = await api.demoLogin(role); localStorage.setItem('llmshield_token', r.access_token); setStatus(`Signed in as ${r.user.email} (${r.user.role})`); } catch { setStatus('Backend unavailable - demo UI still visible'); } }
  return <div className="max-w-2xl"><PageHeader eyebrow="Local demo authentication" title="Sign in"/><Card><p className="text-slate-400">JWT/RBAC is available for local evaluation with admin, analyst, and viewer roles. Enterprise SSO is not included.</p><div className="mt-6 grid gap-3 md:grid-cols-3"><button className="btn" onClick={() => demo('admin')}>Admin demo</button><button className="btn btn-secondary" onClick={() => demo('analyst')}>Analyst demo</button><button className="btn btn-secondary" onClick={() => demo('viewer')}>Viewer demo</button></div><p className="mt-4 text-sm text-sky-200">{status}</p></Card></div>;
}
