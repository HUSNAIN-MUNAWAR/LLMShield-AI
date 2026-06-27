export function StatCard({ label, value, helper }: { label: string; value: string; helper: string }) {
  return (
    <div className="card">
      <div className="text-sm text-slate-400">{label}</div>
      <div className="mt-3 text-3xl font-bold text-white">{value}</div>
      <div className="mt-2 text-sm text-slate-500">{helper}</div>
    </div>
  );
}
