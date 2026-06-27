export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type ScanStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
export type Target = { id: string; name: string; type: string; url?: string | null; endpoint_url?: string | null; safe_mode?: boolean; created_at?: string };
export type AttackPack = { id: string; name: string; category: string; tests: unknown[]; severity_default: Severity; attack_pack_version?: string; tags?: string[] };
export type Scan = { id: string; name?: string; target_id?: string; status: ScanStatus; risk_score?: number; progress?: number; current_test?: string | null; total_tests?: number; passed_tests?: number; failed_tests?: number };
export type Finding = { id: string | number; scan_id?: string | number; test_name?: string; detector_name?: string; severity: Severity; category: string; prompt: string; response: string; evidence?: string; mitigation?: string; risk_score?: number };
export type ProviderHealth = { provider: string; configured: boolean; healthy: boolean; message: string; model?: string };
export type AuditLog = { id: string | number; action: string; actor?: string; role?: string; resource_type?: string; timestamp?: string; details?: Record<string, unknown> };
