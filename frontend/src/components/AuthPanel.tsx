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
        className="rounded-md bg-accent px-3.5 py-1.5 text-sm font-medium text-on-accent transition-colors hover:bg-accent-bright"
      >
        Sign in
      </button>
    )
  }

  return (
    <div className="flex items-center gap-3">
      <img
        src={user.avatar_url}
        alt=""
        className="h-7 w-7 rounded-full ring-2 ring-accent/30"
      />
      <span className="text-sm text-text-bright">{user.username}</span>
      <button
        type="button"
        onClick={() => logout()}
        className="text-sm text-text-dim transition-colors hover:text-text-bright"
      >
        Sign out
      </button>
    </div>
  )
}
