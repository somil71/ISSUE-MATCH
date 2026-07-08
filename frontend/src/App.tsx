import { useQuery } from '@tanstack/react-query'
import { apiGet, type HealthStatus } from './lib/api'
import { AuthPanel } from './components/AuthPanel'
import { RepoWorkspace } from './components/RepoWorkspace'
import { SkillProfile } from './components/SkillProfile'
import { useSession } from './lib/session'

function StatusDot({ ok }: { ok: boolean | undefined }) {
  const color = ok === undefined ? 'bg-text-dim' : ok ? 'bg-safe' : 'bg-danger'
  return <span className={`inline-block h-2 w-2 rounded-full ${color}`} />
}

function App() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiGet<HealthStatus>('/health'),
    refetchInterval: 15_000,
  })
  const { data: user } = useSession()

  return (
    <div className="mx-auto min-h-svh max-w-5xl px-6 py-16">
      <header className="mb-10 flex items-start justify-between gap-6">
        <div>
          <h1 className="text-2xl font-semibold text-text-bright">
            IssueMatch AI
          </h1>
          <p className="mt-1 text-sm text-text-dim">
            Find the right open-source issue for the right contributor — and
            know exactly why it's safe to touch.
          </p>
        </div>
        <AuthPanel />
      </header>

      <section className="rounded-lg border border-border bg-surface-1 p-6">
        <h2 className="text-sm font-medium text-text-bright">
          System status
        </h2>
        <div className="mt-4 flex flex-col gap-3 text-sm">
          <div className="flex items-center justify-between">
            <span>API</span>
            <span className="flex items-center gap-2">
              <StatusDot ok={isLoading ? undefined : !isError} />
              <span className="metric text-text-dim">
                {isLoading ? 'checking…' : isError ? 'unreachable' : 'ok'}
              </span>
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span>Database</span>
            <span className="flex items-center gap-2">
              <StatusDot ok={data && data.services.database === 'ok'} />
              <span className="metric text-text-dim">
                {data?.services.database ?? '—'}
              </span>
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span>Cache</span>
            <span className="flex items-center gap-2">
              <StatusDot ok={data && data.services.cache === 'ok'} />
              <span className="metric text-text-dim">
                {data?.services.cache ?? '—'}
              </span>
            </span>
          </div>
        </div>
      </section>

      {user && (
        <>
          <SkillProfile user={user} />
          <RepoWorkspace />
        </>
      )}
    </div>
  )
}

export default App
