'use client';

import { createContext, useContext, useMemo } from 'react';

type Messages = Record<string, string>;

const I18nContext = createContext<{ messages: Messages; locale: string } | null>(null);

export function I18nProvider({ 
  messages, 
  locale, 
  children 
}: { 
  messages: Messages; 
  locale: string; 
  children: React.ReactNode;
}) {
  const value = useMemo(() => ({ messages, locale }), [messages, locale]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}

export function useTranslations(namespace?: string) {
  const { messages } = useI18n();
  return (key: string) => {
    const fullKey = namespace ? `${namespace}.${key}` : key;
    return messages[fullKey] || key;
  };
}

export function useLocale() {
  const { locale } = useI18n();
  return locale;
}

