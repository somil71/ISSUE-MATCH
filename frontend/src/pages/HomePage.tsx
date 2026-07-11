import { RepoWorkspace } from '../components/RepoWorkspace'
import { LandingHero } from '../components/LandingHero'
import type { CurrentUser } from '../lib/api'

export function HomePage({ user }: { user: CurrentUser | null | undefined }) {
  if (!user) {
    return <LandingHero />
  }

  return (
    <>
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text-bright">
          Welcome back, {user.username}
        </h1>
        <p className="mt-1 text-sm text-text-dim">
          Set your skills, then point the engine at a repo to see what's safe
          to touch.
        </p>
      </div>

      <RepoWorkspace user={user} />
    </>
  )
}
