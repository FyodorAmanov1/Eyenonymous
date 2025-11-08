import ThemeToggle from '@/components/nav/ThemeToggle';
import LanguageSwitcher from '@/components/nav/LanguageSwitcher';
import { useTranslations } from '@/providers/I18nProvider';

export default function Topbar({ onMenuClick }: { onMenuClick?: () => void }) {
    const t = useTranslations();
    return (
      <header className="h-12 border-b border-border flex items-center justify-between px-2 sm:px-4 bg-surface">
        <div className="flex items-center gap-1.5 sm:gap-2 min-w-0 flex-1">
          <button
            type="button"
            onClick={onMenuClick}
            className="sm:hidden h-7 px-2 rounded border border-border bg-surface text-foreground text-xs transition-base hover:bg-surface-2 hover-scale flex-shrink-0"
            aria-label="Open menu"
          >
            {t('topbar.menu')}
          </button>
          <div className="text-xs sm:text-sm text-muted truncate">
            {t('topbar.jetson')} <span className="text-positive font-medium animate-pulse-subtle">{t('topbar.online')}</span>
          </div>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-3 flex-shrink-0">
          <div className="text-xs text-muted hidden md:block hover:text-accent transition-base">
            {t('topbar.builtBy')}
          </div>
          <LanguageSwitcher />
          <ThemeToggle />
        </div>
      </header>
    );
  }