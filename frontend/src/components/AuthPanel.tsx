import { loginWithGitHub, useSession } from '../lib/session'

export function AuthPanel() {
  const { data: user, isLoading, logout } = useSession()

  if (isLoading) {
    return <span className="text-sm text-text-dim">checking session…</span>
  }

  if (!user) {
    return (
      <button
        type="button"
        onClick={loginWithGitHub}
        className="rounded-md bg-surface-2 px-4 py-2 text-sm font-medium text-text-bright hover:bg-border"
      >
        Sign in with GitHub
      </button>
    )
  }

  return (
    <div className="flex items-center gap-3">
      <img
        src={user.avatar_url}
        alt=""
        className="h-8 w-8 rounded-full border border-border"
      />
      <span className="text-sm text-text-bright">{user.username}</span>
      <button
        type="button"
        onClick={() => logout()}
        className="text-sm text-text-dim hover:text-text-bright"
      >
        Sign out
      </button>
    </div>
  )
}
