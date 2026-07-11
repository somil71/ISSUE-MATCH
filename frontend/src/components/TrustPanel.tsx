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
      className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-surface-2"
      title={`Zero-external-AI guarantee — live list of hosts actually contacted this session: ${label}`}
    >
      <ShieldIcon className={`h-4 w-4 ${onlyGithub ? 'text-safe' : 'text-danger'}`} />
    </div>
  )
}
