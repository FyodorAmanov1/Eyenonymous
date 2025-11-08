import { prisma } from '@/lib/prisma';
import { getTranslations } from '@/lib/i18n-server';

export const dynamic = 'force-dynamic';

export default async function EventsPage() {
  const t = await getTranslations();
  const detections = await prisma.detection.findMany({
    orderBy: { createdAt: 'desc' },
    take: 100,
  });

  return (
    <div className="bg-surface border border-border rounded-lg p-4 animate-fade-in">
      <h1 className="text-lg font-semibold mb-4">{t('events.title')}</h1>
      <table className="w-full text-xs">
        <thead className="text-muted">
          <tr className="text-left border-b border-border">
            <th className="py-2">{t('events.time')}</th>
            <th>{t('events.device')}</th>
            <th>{t('events.scene')}</th>
            <th>{t('events.labels')}</th>
          </tr>
        </thead>
        <tbody>
          {detections.map((d: { id: number; createdAt: Date; deviceId: string; scene: string | null; labels: any }, idx: number) => (
            <tr
              key={d.id}
              className="border-b border-border transition-base hover:bg-surface-2 animate-slide-in-right"
              style={{ animationDelay: `${idx * 20}ms` }}
            >
              <td className="py-2">
                {new Date(d.createdAt).toLocaleString()}
              </td>
              <td className="transition-base hover:text-accent">{d.deviceId}</td>
              <td>{d.scene ?? '-'}</td>
              <td>
                {Array.isArray(d.labels)
                  ? d.labels.map((l: any) => l.name).join(', ')
                  : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}