import Skeleton from '@/components/skeletons/Skeleton';

export default function LiveSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1.6fr_0.4fr] gap-4">
      <div className="space-y-4">
        <Skeleton className="w-full aspect-video" />
        <div className="bg-surface border border-border rounded-lg p-4">
          <Skeleton className="h-4 w-32 mb-2" />
          <Skeleton className="h-3 w-72" />
        </div>
      </div>
      <div className="bg-surface border border-border rounded-lg p-4 h-[calc(100vh-6rem)] overflow-y-auto">
        <Skeleton className="h-4 w-40 mb-4" />
        <div className="flex flex-col gap-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="p-2 border border-border rounded bg-surface-2">
              <Skeleton className="h-3 w-48 mb-2" />
              <div className="flex gap-2">
                <Skeleton className="h-5 w-16 rounded" />
                <Skeleton className="h-5 w-20 rounded" />
                <Skeleton className="h-5 w-14 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


