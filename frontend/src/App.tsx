import { AuthPanel } from './components/AuthPanel'
import { LandingHero } from './components/LandingHero'
import { Logo } from './components/Logo'
import { RepoWorkspace } from './components/RepoWorkspace'
import { SkillProfile } from './components/SkillProfile'
import { SystemStatus } from './components/SystemStatus'
import { TrustPanel } from './components/TrustPanel'
import { useSession } from './lib/session'

function App() {
  const { data: user } = useSession()

  return (
    <div className="min-h-svh">
      <header className="sticky top-0 z-10 border-b border-border bg-surface-0/85 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3.5">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent-bg text-accent">
              <Logo className="h-4 w-4" />
            </div>
            <span className="font-semibold text-text-bright">
              IssueMatch AI
            </span>
          </div>
          <div className="flex items-center gap-5">
            <TrustPanel />
            <SystemStatus />
            <AuthPanel />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        {!user ? (
          <LandingHero />
        ) : (
          <>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-text-bright">
                Welcome back, {user.username}
              </h1>
              <p className="mt-1 text-sm text-text-dim">
                Set your skills, then point the engine at a repo to see what's
                safe to touch.
              </p>
            </div>
            <SkillProfile user={user} />
            <RepoWorkspace />
          </>
        )}
      </main>
    </div>
  )
}

export default App
