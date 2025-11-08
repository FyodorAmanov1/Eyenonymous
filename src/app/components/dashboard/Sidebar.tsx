'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from '@/providers/I18nProvider';

const items = [
  { href: '/live', key: 'nav.live' },
  { href: '/events', key: 'nav.events' },
  { href: '/analytics', key: 'nav.analytics' },
  { href: '/admin', key: 'nav.admin' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations();
  return (
    <aside className="w-56 h-full bg-surface border-r border-border p-4 flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-bold">{t('sidebar.title')}</h1>
        <p className="text-xs text-muted">{t('sidebar.subtitle')}</p>
      </div>
      <nav className="flex flex-col gap-2">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded px-3 py-2 text-sm transition-base ${
                active
                  ? 'bg-surface-2 text-foreground'
                  : 'text-muted hover:bg-surface-2 hover:text-accent hover-lift'
              }`}
            >
              {t(item.key as any)}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}