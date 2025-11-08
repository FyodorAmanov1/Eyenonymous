'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useLocale, useTranslations } from '@/providers/I18nProvider';
import { Globe, ChevronDown, X } from 'lucide-react';
import ReactCountryFlag from 'react-country-flag';

const languages = [
  { code: 'en', label: 'English', flag: 'US' },
  { code: 'ko', label: '한국어', flag: 'KR' },
];

export default function LanguageSwitcher() {
  const t = useTranslations();
  const router = useRouter();
  const locale = useLocale();
  const [isOpen, setIsOpen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  function switchTo(next: string) {
    const oneYear = 60 * 60 * 24 * 365;
    document.cookie = `NEXT_LOCALE=${next}; Path=/; Max-Age=${oneYear}`;
    setIsOpen(false);
    router.refresh();
  }

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const currentLang = languages.find((l) => l.code === locale) || languages[0];

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onTouchStart={() => setShowTooltip(true)}
        onTouchEnd={() => setTimeout(() => setShowTooltip(false), 2000)}
        className="h-7 sm:h-8 px-1.5 sm:px-2 rounded border border-border bg-surface text-foreground inline-flex items-center gap-1 sm:gap-1.5 hover:bg-surface-2 active:bg-surface-2 transition-base hover-scale relative touch-manipulation"
        aria-label={t('language.change')}
        aria-expanded={isOpen}
      >
        <div className="relative flex-shrink-0">
          <Globe className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
        </div>
        <div className="relative w-3.5 h-3.5 flex-shrink-0">
          <X
            className={`absolute inset-0 w-3.5 h-3.5 transition-all duration-200 ${
              isOpen ? 'opacity-100 rotate-0' : 'opacity-0 rotate-90'
            }`}
          />
          <ChevronDown
            className={`absolute inset-0 w-3.5 h-3.5 transition-all duration-200 ${
              isOpen ? 'opacity-0 -rotate-90' : 'opacity-100 rotate-0'
            }`}
          />
        </div>
        {showTooltip && (
          <div className="absolute top-full right-0 mt-2 px-2 py-1 text-xs bg-foreground text-background rounded whitespace-nowrap z-50 pointer-events-none animate-scale-in">
            {t('language.change')}
            <div className="absolute bottom-full right-2 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-foreground" />
          </div>
        )}
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-1 bg-surface border border-border rounded shadow-lg z-50 min-w-[140px] sm:min-w-[160px] overflow-hidden animate-scale-in">
          {languages.map((lang, idx) => (
            <button
              key={lang.code}
              type="button"
              onClick={() => switchTo(lang.code)}
              className={`w-full px-3 py-2 text-left text-sm inline-flex items-center gap-2 transition-base ${
                locale === lang.code
                  ? 'bg-surface-2 text-foreground'
                  : 'text-muted hover:bg-surface-2 hover:text-foreground hover-lift'
              }`}
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <ReactCountryFlag
                svg
                countryCode={lang.flag}
                style={{ width: '1em', height: '1em' }}
              />
              <span>{lang.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
