import { Navigate } from 'react-router-dom'
import { SectionCard } from '../components/SectionCard'
import { SkillProfile } from '../components/SkillProfile'
import { TagIcon } from '../components/Icons'
import { useSession } from '../lib/session'

export function SettingsPage() {
  const { data: user, isLoading } = useSession()

  if (isLoading) {
    return <p className="mt-10 text-sm text-text-dim">Loading…</p>
  }

  if (!user) {
    return <Navigate to="/" replace />
  }

  return (
    <>
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text-bright">
          Settings
        </h1>
        <p className="mt-1 text-sm text-text-dim">
          Your account and the skill profile issue matching compares against.
        </p>
      </div>

      <SectionCard
        icon={<TagIcon />}
        title="Account"
        description="Identity comes from GitHub — there's no separate password to manage."
        accent="violet"
      >
        <div className="flex items-center gap-3">
          <img
            src={user.avatar_url}
            alt=""
            className="h-12 w-12 rounded-full ring-2 ring-accent/30"
          />
          <div>
            <p className="text-sm font-medium text-text-bright">
              {user.username}
            </p>
            <a
              href={`https://github.com/${user.username}`}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-accent-bright hover:underline"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </SectionCard>

      <SkillProfile user={user} />
    </>
  )
}
