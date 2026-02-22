import clsx from 'clsx';
import type React from 'react';

interface SkeletonProps { className?: string; style?: React.CSSProperties }

export function Skeleton({ className, style }: SkeletonProps) {
  return <div className={clsx('animate-pulse bg-gray-200 rounded', className)} style={style} />;
}

export function PatientCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
      <div className="h-32 bg-gray-200 animate-pulse" />
      <div className="p-5 space-y-3">
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-3 w-1/2" />
        <Skeleton className="h-3 w-2/3" />
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          {Array.from({ length: cols }).map((_, j) => (
            <Skeleton key={j} className="h-4 flex-1"
              style={{ animationDelay: `${(i * cols + j) * 50}ms` }} />
          ))}
        </div>
      ))}
    </div>
  );
}
