import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiGet, type BlastMapNode, type BlastMapResponse } from '../lib/api'
import { BlastMapSkeleton } from './Skeleton'

const RING_STEP = 74
const CENTER = 320
const NODE_RADIUS = 15

interface Positioned extends BlastMapNode {
  x: number
  y: number
}

/** Deterministic radial layout: rings by hop distance (BFS depth over the
 * real reverse call graph), nodes spread evenly around each ring, rotated
 * per ring so consecutive hops don't stack directly on top of each other. */
function layoutRings(nodes: BlastMapNode[]): Positioned[] {
  const byHop = new Map<number, BlastMapNode[]>()
  for (const node of nodes) {
    const ring = byHop.get(node.hops) ?? []
    ring.push(node)
    byHop.set(node.hops, ring)
  }

  const positioned: Positioned[] = []
  for (const [hop, ring] of byHop) {
    if (hop === 0) {
      positioned.push({ ...ring[0], x: CENTER, y: CENTER })
      continue
    }
    const radius = hop * RING_STEP
    const rotation = (hop * 27 * Math.PI) / 180
    ring.forEach((node, i) => {
      const angle = (i / ring.length) * 2 * Math.PI + rotation
      positioned.push({
        ...node,
        x: CENTER + radius * Math.cos(angle),
        y: CENTER + radius * Math.sin(angle),
      })
    })
  }
  return positioned
}

function bucketColor(bucket: string | null): string {
  if (bucket === 'here_be_dragons') return 'var(--color-danger)'
  if (bucket === 'start_here') return 'var(--color-safe)'
  return 'var(--color-text-dim)'
}

function truncate(label: string, max: number): string {
  return label.length > max ? `${label.slice(0, max - 1)}…` : label
}

export function BlastRadiusMap({
  owner,
  name,
  functionId,
  onClose,
}: {
  owner: string
  name: string
  functionId: string
  onClose: () => void
}) {
  const [focusId, setFocusId] = useState(functionId)

  const map = useQuery({
    queryKey: ['blast-map', owner, name, focusId],
    queryFn: () =>
      apiGet<BlastMapResponse>(
        `/repos/${owner}/${name}/blast-map/${encodeURIComponent(focusId)}?hops=3`,
      ),
  })

  const positioned = useMemo(() => layoutRings(map.data?.nodes ?? []), [map.data])
  const byId = useMemo(() => new Map(positioned.map((n) => [n.id, n])), [positioned])
  const maxHop = useMemo(
    () => Math.max(0, ...(map.data?.nodes.map((n) => n.hops) ?? [0])),
    [map.data],
  )
  const viewSize = CENTER * 2
  const focusNode = byId.get(focusId)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        className="flex max-h-[85vh] w-full max-w-3xl flex-col overflow-hidden rounded-xl border border-border bg-surface-1/80 shadow-2xl shadow-black/40 backdrop-blur-md"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
          <div>
            <h3 className="text-sm font-semibold text-text-bright">
              Blast Radius Map
            </h3>
            <p className="mt-1 text-xs text-text-dim">
              Real transitive dependents, traced through the actual call
              graph — each ring is one more hop away. Click a node to
              re-center the map on it.
            </p>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 rounded-md px-2 py-1 text-xs text-text-dim hover:text-text-bright"
          >
            Close
          </button>
        </div>

        <div className="flex-1 overflow-auto p-5">
          {focusId !== functionId && (
            <button
              onClick={() => setFocusId(functionId)}
              className="metric mb-3 rounded-full bg-surface-2 px-2.5 py-1 text-xs text-text-dim hover:text-text-bright"
            >
              ← back to {functionId.split('::')[1]?.split(':')[0] ?? functionId}
            </button>
          )}

          {map.isPending && (
            <>
              <p className="text-sm text-text-dim">
                Tracing the dependency graph…
              </p>
              <BlastMapSkeleton />
            </>
          )}
          {map.isError && (
            <p className="text-sm text-danger">
              Could not load the graph for this function.
            </p>
          )}

          {map.isSuccess && (
            <>
              <div
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs ${
                  map.data.total_transitive_dependents > 0
                    ? 'bg-danger-bg text-danger'
                    : 'bg-safe-bg text-safe'
                }`}
              >
                <span className="metric font-semibold">
                  {map.data.total_transitive_dependents}
                </span>
                <span>
                  function
                  {map.data.total_transitive_dependents === 1 ? '' : 's'}{' '}
                  transitively depend on{' '}
                  <span className="metric font-medium">
                    {focusNode?.name ?? focusId}
                  </span>
                  {map.data.total_transitive_dependents > 0
                    ? ' — everything shown here could break if it changes.'
                    : " — it's a safe leaf in the real call graph."}
                </span>
              </div>

              <svg
                viewBox={`0 0 ${viewSize} ${viewSize}`}
                className="mt-3 h-[70vh] w-full sm:h-[32rem]"
              >
              {Array.from({ length: maxHop }, (_, i) => i + 1).map((hop) => (
                <circle
                  key={hop}
                  cx={CENTER}
                  cy={CENTER}
                  r={hop * RING_STEP}
                  fill="none"
                  stroke="var(--color-border)"
                  strokeDasharray="2 5"
                />
              ))}
              {map.data.edges.map((edge, i) => {
                const source = byId.get(edge.source)
                const target = byId.get(edge.target)
                if (!source || !target) return null
                return (
                  <line
                    key={i}
                    x1={source.x}
                    y1={source.y}
                    x2={target.x}
                    y2={target.y}
                    stroke="var(--color-border-bright)"
                    strokeWidth={1}
                    opacity={0.7}
                  />
                )
              })}
              {positioned.map((node) => (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  className="cursor-pointer"
                  onClick={() => setFocusId(node.id)}
                >
                  <circle
                    r={node.id === focusId ? NODE_RADIUS + 4 : NODE_RADIUS}
                    fill={
                      node.id === focusId
                        ? 'var(--color-accent-bright)'
                        : bucketColor(node.bucket)
                    }
                    opacity={node.id === focusId ? 1 : 0.85}
                    stroke="var(--color-surface-0)"
                    strokeWidth={2}
                  />
                  <title>
                    {`${node.name} — ${node.file}:${node.start_line} (score ${node.score.toFixed(2)}, ${node.hops} hop${node.hops === 1 ? '' : 's'} away)`}
                  </title>
                  <text
                    y={NODE_RADIUS + 13}
                    textAnchor="middle"
                    style={{ fill: 'var(--color-text-dim)', fontSize: '9px' }}
                    className="metric"
                  >
                    {truncate(node.name, 14)}
                  </text>
                </g>
              ))}
              </svg>

              <div className="mt-4 flex flex-wrap items-center gap-4 border-t border-border pt-3 text-xs text-text-dim">
                <span className="flex items-center gap-1.5">
                  <span className="h-3 w-3 rounded-full bg-accent-bright" />
                  Origin node
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-3 w-3 rounded-full bg-danger" />
                  Here Be Dragons
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-3 w-3 rounded-full bg-safe" />
                  Start Here
                </span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
