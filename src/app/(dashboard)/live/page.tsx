'use client';

import { Suspense } from 'react';
import { useSuspenseQuery } from '@tanstack/react-query';
import LivePlayer from '@/components/dashboard/live/LivePlayer';
import LiveSkeleton from '@/components/skeletons/LiveSkeleton';
import { useTranslations } from '@/providers/I18nProvider';

type Detection = {
  id: number;
  deviceId: string;
  scene?: string | null;
  labels: any;
  createdAt: string;
};

function useDetections(limit: number) {
  return useSuspenseQuery<{ detections: Detection[] }, Error, Detection[]>({
    queryKey: ['detections', limit],
    queryFn: async (): Promise<{ detections: Detection[] }> => {
      // Check for demo mode
      const demoMode = typeof window !== 'undefined' 
        ? localStorage.getItem('demoMode') === 'true'
        : false;
      
      // Use absolute URL to avoid SSR issues
      const baseUrl = typeof window !== 'undefined' 
        ? window.location.origin 
        : process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';
      const url = `${baseUrl}/api/detections?limit=${limit}${demoMode ? '&demo=true' : ''}`;
      
      const res = await fetch(url, { 
        cache: 'no-store',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) throw new Error('Failed to load detections');
      return (await res.json()) as { detections: Detection[] };
    },
    refetchInterval: 2000,
    refetchIntervalInBackground: true,
    staleTime: 1000,
    select: (data) => data.detections,
  });
}

function LiveContent() {
  const t = useTranslations();
  const { data: detections } = useDetections(20);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1.6fr_0.4fr] gap-4">
      <div className="space-y-4">
        <LivePlayer relayHost={process.env.NEXT_PUBLIC_RELAY_HOST || 'http://localhost:3001'} />
        <div className="bg-surface border border-border rounded-lg p-4">
          <h2 className="text-sm font-semibold mb-2">{t('live.sceneSummary')}</h2>
          <p className="text-xs text-muted">
            {t('live.latestScene')}: {detections[0]?.scene ?? 'unknown / not provided by Jetson'}
          </p>
        </div>
      </div>
      <div className="bg-surface border border-border rounded-lg p-4 h-[calc(100vh-6rem)] overflow-y-auto animate-fade-in">
        <h2 className="text-sm font-semibold mb-4">{t('live.latestDetections')}</h2>
        <div className="flex flex-col gap-2">
          {detections.map((det: Detection, idx: number) => (
            <div
              key={det.id}
              className="text-xs bg-surface-2 rounded border border-border p-2 transition-base hover:bg-accent-ghost hover-lift animate-slide-in-right"
              style={{ animationDelay: `${idx * 30}ms` }}
            >
              <div className="flex justify-between">
                <span className="font-medium text-foreground hover:text-accent transition-base">
                  {det.deviceId}
                </span>
                <span className="text-muted">
                  {new Date(det.createdAt).toLocaleTimeString()}
                </span>
              </div>
              <div className="mt-1 flex gap-1 flex-wrap">
                {(det.labels || []).map((l: any, labelIdx: number) => (
                  <span
                    key={labelIdx}
                    className="px-2 py-0.5 bg-surface-2 rounded text-foreground transition-base hover:bg-accent-ghost"
                  >
                    {l.name} {l.conf ? `(${Math.round(l.conf * 100)}%)` : ''}
                  </span>
                ))}
              </div>
              {det.scene ? (
                <p className="text-muted mt-1">scene: {det.scene}</p>
              ) : null}
            </div>
          ))}
          {detections.length === 0 && (
            <p className="text-xs text-muted">{t('live.noDetections')}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function LivePage() {
  return (
    <Suspense fallback={<LiveSkeleton />}>
      <LiveContent />
    </Suspense>
  );
}