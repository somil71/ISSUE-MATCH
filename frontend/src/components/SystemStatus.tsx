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
    <div className="flex items-center gap-1.5" title={label}>
      <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} />
      <span className="hidden text-xs text-text-dim sm:inline">
        {isLoading ? 'Checking…' : ok ? 'All systems operational' : 'Degraded'}
      </span>
    </div>
  )
}
