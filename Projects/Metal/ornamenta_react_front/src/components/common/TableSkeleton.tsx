import React from "react";
import { Skeleton } from "@heroui/react";

type TableSkeletonProps = {
  rows?: number;
  columns?: number;
  showActions?: boolean;
};

export const TableSkeleton: React.FC<TableSkeletonProps> = ({
  rows = 5,
  columns = 4,
  showActions = true,
}) => {
  return (
    <div className="space-y-3">
      {/* Header skeleton */}
      <div className="flex gap-4 p-4 bg-default-50 rounded-t-lg">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={`header-${i}`} className="h-6 rounded-lg flex-1" />
        ))}
        {showActions && <Skeleton className="h-6 rounded-lg w-32" />}
      </div>

      {/* Rows skeleton */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={`row-${rowIndex}`}
          className="flex gap-4 p-4 bg-default-50/50 rounded-lg animate-pulse"
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton
              key={`cell-${rowIndex}-${colIndex}`}
              className="h-4 rounded-lg flex-1"
            />
          ))}
          {showActions && (
            <div className="flex gap-2 w-32">
              <Skeleton className="h-8 w-16 rounded-md" />
              <Skeleton className="h-8 w-16 rounded-md" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
