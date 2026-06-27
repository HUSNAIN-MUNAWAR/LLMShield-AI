const links = [
  ['/', 'Dashboard'], ['/targets', 'Targets'], ['/attack-packs', 'Attack Packs'], ['/scans', 'Scans'], ['/findings', 'Findings'], ['/reports', 'Reports'], ['/audit-logs', 'Audit Logs'], ['/settings', 'Settings'], ['/docs', 'Docs']
];
export function Sidebar() {
  return <aside className="sticky top-0 hidden h-screen w-72 border-r border-slate-800/80 bg-slate-950 p-6 lg:block"><div className="mb-8"><div className="text-xl font-black text-white">LLMShield AI</div><p className="mt-2 text-xs text-slate-400">Authorized GenAI security testing only</p></div><nav className="space-y-2">{links.map(([href,label]) => <a key={href} href={href} className="block rounded-xl px-4 py-3 text-sm font-bold text-slate-300 hover:bg-slate-900 hover:text-white">{label}</a>)}</nav><div className="absolute bottom-6 left-6 right-6 rounded-xl border border-sky-400/20 bg-sky-400/10 p-4 text-xs text-sky-100"><b>Demo auth:</b><br />admin / analyst / viewer roles are local-only examples.</div></aside>;
}
