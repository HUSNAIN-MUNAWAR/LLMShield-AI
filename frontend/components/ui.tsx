import type { ReactNode } from 'react';

export function PageHeader({ title, eyebrow, children }: { title: string; eyebrow?: string; children?: ReactNode }) {
  return <div className="mb-8 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between"><div>{eyebrow && <p className="text-sm font-bold uppercase tracking-[0.25em] text-sky-300">{eyebrow}</p>}<h1 className="mt-2 text-3xl font-black tracking-tight text-white lg:text-5xl">{title}</h1></div>{children}</div>;
}
export function Card({ children, className = '' }: { children: ReactNode; className?: string }) { return <section className={`card p-5 ${className}`}>{children}</section>; }
export function SeverityBadge({ value }: { value: string }) { return <span className={`badge badge-${value.toLowerCase()}`}>{value}</span>; }
export function ProgressBar({ value }: { value: number }) { return <div className="h-2 rounded-full bg-slate-800"><div className="h-2 rounded-full bg-sky-400" style={{ width: `${Math.max(0, Math.min(value, 100))}%` }} /></div>; }
export function Stat({ label, value, hint }: { label: string; value: string; hint: string }) { return <Card><p className="text-sm text-slate-400">{label}</p><p className="mt-2 text-3xl font-black text-white">{value}</p><p className="mt-2 text-sm text-slate-500">{hint}</p></Card>; }
