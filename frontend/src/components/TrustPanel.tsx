import { useQuery } from '@tanstack/react-query'
import { apiGet, type NetworkTrustSummary } from '../lib/api'
import { ShieldIcon } from './Icons'

const ALLOWED_HOST_SUFFIX = 'github.com'

export function TrustPanel() {
  const { data } = useQuery({
    queryKey: ['trust'],
    queryFn: () => apiGet<NetworkTrustSummary>('/trust/network'),
    refetchInterval: 4000,
  })

  const hosts = data?.hosts ?? []
  const onlyGithub = hosts.every((h) => h.host.endsWith(ALLOWED_HOST_SUFFIX))
  const label =
    hosts.length === 0
      ? 'no external calls yet'
      : `${hosts.map((h) => h.host).join(', ')} only`

  return (
    <div
      className="flex items-center gap-1.5"
      title={`This backend's only allowed outbound HTTP calls are to GitHub — live list of hosts actually contacted this session: ${label}`}
    >
      <ShieldIcon className={`h-3.5 w-3.5 ${onlyGithub ? 'text-safe' : 'text-danger'}`} />
      <span className="metric hidden text-xs text-text-dim sm:inline">{label}</span>
    </div>
  )
}
