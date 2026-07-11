function Bar({ className = '' }: { className?: string }) {
  return (
    <div
      className={`rounded-md bg-surface-2 motion-safe:animate-pulse ${className}`}
    />
  )
}

/** Shape-matched placeholder for the analyze results: a summary line, a
 * slider row, and a handful of table rows — so the layout doesn't jump once
 * real data arrives. */
export function AnalyzeResultsSkeleton() {
  return (
    <div className="mt-4">
      <Bar className="h-4 w-64" />
      <Bar className="mt-2 h-4 w-48" />
      <Bar className="mt-4 h-2 w-40" />
      <div className="mt-3 overflow-hidden rounded-md border border-border">
        <div className="h-8 bg-surface-2" />
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="flex items-center gap-4 border-t border-border px-3 py-3"
          >
            <Bar className="h-3 w-24" />
            <Bar className="h-3 w-32" />
            <Bar className="h-3 flex-1" />
            <Bar className="h-3 w-12" />
          </div>
        ))}
      </div>
    </div>
  )
}

/** Shape-matched placeholder for the ranked issue list. */
export function IssueListSkeleton() {
  return (
    <div className="mt-4 flex flex-col gap-3">
      {[0, 1, 2].map((i) => (
        <div key={i} className="rounded-lg border border-border p-4">
          <Bar className="h-4 w-2/3" />
          <Bar className="mt-3 h-3 w-1/3" />
          <Bar className="mt-2 h-3 w-full" />
          <Bar className="mt-2 h-3 w-4/5" />
        </div>
      ))}
    </div>
  )
}

/** Shape-matched placeholder for the Blast Radius Map's radial graph. */
export function BlastMapSkeleton() {
  return (
    <div className="mt-3 flex h-[70vh] w-full items-center justify-center sm:h-[32rem]">
      <div className="relative h-56 w-56">
        <div className="absolute inset-0 rounded-full border border-dashed border-border" />
        <div className="absolute inset-8 rounded-full border border-dashed border-border" />
        <div className="absolute inset-0 flex items-center justify-center">
          <Bar className="h-9 w-9 rounded-full" />
        </div>
      </div>
    </div>
  )
}
