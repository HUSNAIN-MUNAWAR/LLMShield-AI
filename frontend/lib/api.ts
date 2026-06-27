import type { AttackPack, AuditLog, Finding, ProviderHealth, Scan, Target } from './types';

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('llmshield_token') : null;
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init.headers || {})
    },
    cache: 'no-store'
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) => request<{ access_token: string; token_type: string; user: { email: string; role: string } }>('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  demoLogin: (role = 'analyst') => request<{ access_token: string; token_type: string; user: { email: string; role: string } }>(`/api/auth/demo-login?role=${role}`, { method: 'POST' }),
  me: () => request<{ email: string; role: string }>('/api/auth/me'),
  health: () => request<{ status: string }>('/health'),
  providerHealth: (provider = 'mock') => request<ProviderHealth>(`/api/providers/${provider}/health`),
  providers: () => request<ProviderHealth[]>('/api/providers'),
  attackPacks: () => request<AttackPack[]>('/api/attack-packs'),
  targets: () => request<Target[]>('/api/targets'),
  createTarget: (payload: Partial<Target>) => request<Target>('/api/targets', { method: 'POST', body: JSON.stringify(payload) }),
  createScan: (payload: { target_id: string; attack_pack_ids: string[]; options?: Record<string, unknown> }) => request<Scan>('/api/scans', { method: 'POST', body: JSON.stringify(payload) }),
  testTarget: (id: string | number) => request<{ ok: boolean; message: string }>(`/api/targets/${id}/test`, { method: 'POST' }),
  scans: () => request<Scan[]>('/api/scans'),
  runScan: (scanId: string | number) => request<Scan>(`/api/scans/${scanId}/run`, { method: 'POST' }),
  scanStatus: (scanId: string | number) => request<Scan>(`/api/scans/${scanId}/status`),
  findings: () => request<Finding[]>('/api/findings'),
  auditLogs: () => request<AuditLog[]>('/api/audit-logs'),
  metrics: async () => {
    const res = await fetch(`${API_BASE}/metrics`, { cache: 'no-store' });
    return res.text();
  }
};
