'use client';

import ErrorMessage from '@/components/ErrorMessage';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return <ErrorMessage message={error.message} onRetry={reset} />;
}


