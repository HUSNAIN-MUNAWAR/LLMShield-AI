import './globals.css';
import type { Metadata } from 'next';
import { Sidebar } from '../components/layout/sidebar';

export const metadata: Metadata = { title: 'LLMShield AI', description: 'Defensive GenAI security evaluation and red-teaming platform' };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><div className="flex min-h-screen"><Sidebar /><main className="flex-1 p-5 lg:p-8">{children}</main></div></body></html>;
}
