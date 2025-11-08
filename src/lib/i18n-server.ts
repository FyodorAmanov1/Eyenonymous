import { cookies, headers } from 'next/headers';

export async function getTranslations() {
  const cookieStore = await cookies();
  const cookieLocale = cookieStore.get('NEXT_LOCALE')?.value;
  const hdrs = await headers();
  const accept = hdrs.get('accept-language') || '';
  const fallback = 'en';
  const headerLocale = accept.split(',')[0]?.slice(0, 2);
  const locale = (cookieLocale === 'ko' || cookieLocale === 'en')
    ? cookieLocale
    : (headerLocale === 'ko' ? 'ko' : fallback);
  
  const messages = (await import(`@/messages/${locale}.json`)).default;
  
  return (key: string) => {
    return messages[key] || key;
  };
}

