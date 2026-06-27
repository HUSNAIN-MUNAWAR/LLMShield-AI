import type { Finding } from '../../lib/types';

export function FindingTable({ findings }: { findings: Finding[] }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-900 text-slate-400">
          <tr><th className="p-4">Finding</th><th>Severity</th><th>Risk</th><th>Category</th><th>Detector</th></tr>
        </thead>
        <tbody>
          {findings.map((f) => (
            <tr key={f.id} className="border-t border-slate-800 bg-slate-950/60">
              <td className="p-4 text-white">{f.test_name}</td>
              <td><span className="badge">{f.severity}</span></td>
              <td>{f.risk_score}</td>
              <td className="max-w-xs truncate">{f.category}</td>
              <td>{f.detector_name}</td>
            </tr>
          ))}
          {findings.length === 0 && <tr><td className="p-6 text-slate-500" colSpan={5}>No findings yet. Run a scan from the New Scan page.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
