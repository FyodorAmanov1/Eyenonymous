"use client";

export default function ErrorMessage({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <div className="bg-surface border border-border rounded p-4 text-sm">
      <p className="text-foreground">Something went wrong.</p>
      {message ? <p className="text-muted mt-1">{message}</p> : null}
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 inline-flex items-center px-3 py-1.5 rounded border border-border bg-surface text-foreground hover:bg-surface-2"
        >
          Try again
        </button>
      ) : null}
    </div>
  );
}


