import { useQuery } from '@tanstack/react-query'
import { apiGet, type HealthStatus } from '../lib/api'

export function SystemStatus() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiGet<HealthStatus>('/health'),
    refetchInterval: 15_000,
  })

  const ok = !isLoading && !isError && data?.status === 'ok'
  const dotColor = isLoading ? 'bg-text-dim' : ok ? 'bg-safe' : 'bg-danger'
  const label = isLoading
    ? 'Checking systems…'
    : isError
      ? 'API unreachable'
      : `API ok · database ${data!.services.database} · cache ${data!.services.cache}`

  return (
    <div className="flex h-8 items-center gap-1.5 px-1" title={label}>
      <span className={`h-2 w-2 rounded-full ${dotColor}`} />
      <span className="hidden text-xs text-text-dim md:inline">
        {isLoading ? 'Checking…' : ok ? 'Operational' : 'Degraded'}
      </span>
    </div>
  )
}
