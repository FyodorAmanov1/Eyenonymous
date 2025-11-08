import {getRequestConfig} from 'next-intl/server';
import type { Locale } from './i18n';

export default getRequestConfig(async ({ locale }: { locale: Locale }) => ({
  messages: (await import(`../messages/${locale}.json`)).default
}));


