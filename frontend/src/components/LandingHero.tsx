import { loginWithGitHub } from '../lib/session'
import { Logo } from './Logo'

const FEATURES = [
  {
    title: 'Blast Radius Engine',
    body: 'Real tree-sitter parsing, call-graph fan-in, cyclomatic complexity, test proximity, and git churn — combined into one transparent score per function.',
  },
  {
    title: 'Skill-matched issues',
    body: 'Local sentence embeddings rank open issues against your skills. Every match shows the overlapping terms that drove it.',
  },
  {
    title: 'Zero external AI',
    body: 'No LLM calls, no hosted inference, no API key. Every number on screen is computed live, in this process, and is fully inspectable.',
  },
]

export function LandingHero() {
  return (
    <div className="flex flex-col items-center py-16 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent-bg text-accent">
        <Logo className="h-7 w-7" />
      </div>
      <h1 className="mt-6 max-w-2xl text-4xl font-semibold tracking-tight text-text-bright">
        Know exactly which issue is safe to touch — before you touch it.
      </h1>
      <p className="mt-4 max-w-xl text-text-dim">
        IssueMatch AI matches you to open-source issues you can actually
        handle, and proves it with static analysis — not a guess, not an LLM.
      </p>
      <button
        type="button"
        onClick={loginWithGitHub}
        className="mt-8 rounded-lg bg-accent px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-accent-bright"
      >
        Sign in with GitHub
      </button>

      <div className="mt-16 grid gap-4 text-left sm:grid-cols-3">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="rounded-xl border border-border bg-surface-1 p-5"
          >
            <h3 className="text-sm font-medium text-text-bright">
              {f.title}
            </h3>
            <p className="mt-2 text-sm text-text-dim">{f.body}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
