import { prisma } from "@/lib/prisma";
import { getTranslations } from '@/lib/i18n-server';

export const dynamic = "force-dynamic";

export default async function AnalyticsPage() {
  const t = await getTranslations();
  // pull last 200 detections
  const detections = await prisma.detection.findMany({
    orderBy: { createdAt: "desc" },
    take: 200,
  });

  // aggregate in JS (fast enough for hackathon size)
  const total = detections.length;

  const byDevice: Record<string, number> = {};
  const labelCounts: Record<string, number> = {};
  const sceneCounts: Record<string, number> = {};

  for (const d of detections) {
    // devices
    byDevice[d.deviceId] = (byDevice[d.deviceId] || 0) + 1;

    // scenes
    if (d.scene) {
      sceneCounts[d.scene] = (sceneCounts[d.scene] || 0) + 1;
    }

    // labels (d.labels is JSON)
    if (Array.isArray(d.labels)) {
      for (const l of d.labels as any[]) {
        const name = l.name ?? "unknown";
        labelCounts[name] = (labelCounts[name] || 0) + 1;
      }
    }
  }

  const topLabels = Object.entries(labelCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  const topScenes = Object.entries(sceneCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">{t('analytics.title')}</h1>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="bg-surface border border-border rounded-lg p-4 animate-fade-in hover-lift" style={{ animationDelay: '0ms' }}>
          <p className="text-xs text-muted mb-1">{t('analytics.totalDetections')}</p>
          <p className="text-3xl font-bold">{total}</p>
        </div>
        <div className="bg-surface border border-border rounded-lg p-4 animate-fade-in hover-lift" style={{ animationDelay: '100ms' }}>
          <p className="text-xs text-muted mb-1">{t('analytics.devices')}</p>
          <ul className="text-xs space-y-1">
            {Object.entries(byDevice).map(([dev, count]) => (
              <li key={dev} className="flex justify-between transition-base hover:text-accent">
                <span>{dev}</span>
                <span className="text-foreground">{count}</span>
              </li>
            ))}
            {Object.keys(byDevice).length === 0 && (
              <li className="text-muted">{t('analytics.noData')}</li>
            )}
          </ul>
        </div>
        <div className="bg-surface border border-border rounded-lg p-4 animate-fade-in hover-lift" style={{ animationDelay: '200ms' }}>
          <p className="text-xs text-muted mb-1">{t('analytics.topScene')}</p>
          {topScenes[0] ? (
            <p className="text-xl font-semibold">{topScenes[0][0]}</p>
          ) : (
            <p className="text-muted text-sm">{t('analytics.noScene')}</p>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="bg-surface border border-border rounded-lg p-4 animate-fade-in hover-lift" style={{ animationDelay: '300ms' }}>
          <h2 className="text-sm font-semibold mb-2">{t('analytics.topLabels')}</h2>
          <ul className="text-xs space-y-1">
            {topLabels.length ? (
              topLabels.map(([label, count], idx) => (
                <li key={label} className="flex justify-between transition-base hover:text-accent" style={{ animationDelay: `${(idx + 1) * 30}ms` }}>
                  <span>{label}</span>
                  <span className="text-foreground">{count}</span>
                </li>
              ))
            ) : (
              <li className="text-muted">{t('analytics.noData')}</li>
            )}
          </ul>
        </div>

        <div className="bg-surface border border-border rounded-lg p-4 animate-fade-in hover-lift" style={{ animationDelay: '400ms' }}>
          <h2 className="text-sm font-semibold mb-2">{t('analytics.scenes')}</h2>
          <ul className="text-xs space-y-1">
            {topScenes.length ? (
              topScenes.map(([scene, count], idx) => (
                <li key={scene} className="flex justify-between transition-base hover:text-accent" style={{ animationDelay: `${(idx + 1) * 30}ms` }}>
                  <span>{scene}</span>
                  <span className="text-foreground">{count}</span>
                </li>
              ))
            ) : (
              <li className="text-muted">{t('analytics.noData')}</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}