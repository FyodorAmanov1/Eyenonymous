'use client';

import { useState } from 'react';
import Sidebar from '@/components/dashboard/Sidebar';
import Topbar from '@/components//nav/Topbar';

export default function DashboardShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Static sidebar on desktop */}
      <div className="hidden lg:block h-screen">
        <Sidebar />
      </div>

      {/* Mobile drawer */}
      <div className="lg:hidden">
        <div
          className={
            `fixed inset-y-0 left-0 w-64 z-40 transform transition-base ` +
            (open ? 'translate-x-0' : '-translate-x-full')
          }
          style={{ transitionDuration: 'var(--duration-base)', transitionTimingFunction: 'var(--easing-smooth)' }}
        >
          <div className="h-full bg-surface border-r border-border animate-scale-in">
            <Sidebar />
          </div>
        </div>
        {open && (
          <button
            aria-label="Close menu"
            onClick={() => setOpen(false)}
            className="fixed inset-0 bg-black/40 z-30 transition-base animate-fade-in"
            style={{ transitionDuration: 'var(--duration-fast)' }}
          />
        )}
      </div>

      <div className="flex-1 flex flex-col">
        <Topbar onMenuClick={() => setOpen(true)} />
        <main className="flex-1 p-4">{children}</main>
      </div>
    </div>
  );
}


