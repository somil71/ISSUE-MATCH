import { Link } from 'react-router-dom'
import { loginWithGitHub } from '../lib/session'
import { TerminalIcon } from './Icons'

const FEATURES = [
  {
    eyebrow: '01 // CORE',
    eyebrowColor: 'text-accent-bright',
    title: 'Blast Radius Engine',
    body: 'Real tree-sitter parsing, call-graph fan-in, cyclomatic complexity, test proximity, and git churn — combined into one transparent score per function.',
  },
  {
    eyebrow: '02 // ALIGNMENT',
    eyebrowColor: 'text-violet',
    title: 'Skill-matched issues',
    body: 'Local sentence embeddings rank open issues against your skills. Every match shows the overlapping terms that drove it.',
  },
  {
    eyebrow: '03 // EXECUTION',
    eyebrowColor: 'text-cyan',
    title: 'Zero external AI',
    body: 'No LLM calls, no hosted inference, no API key. Every number on screen is computed live, in this process, and is fully inspectable.',
  },
]

export function LandingHero() {
  return (
    <div className="relative flex flex-col items-center py-16 text-center">
      <div className="pointer-events-none absolute -top-10 left-1/4 h-72 w-72 rounded-full bg-accent/5 blur-[100px]" />
      <div className="pointer-events-none absolute bottom-0 right-1/4 h-56 w-56 rounded-full bg-violet/5 blur-[90px]" />

      <div className="relative flex h-12 w-12 items-center justify-center rounded-lg border border-border bg-surface-1 text-accent-bright">
        <TerminalIcon className="h-6 w-6" />
      </div>
      <h1 className="relative mt-6 max-w-2xl text-4xl font-black tracking-tight text-text-bright sm:text-5xl">
        Know exactly which issue is{' '}
        <span className="bg-gradient-to-r from-accent-bright to-violet bg-clip-text text-transparent">
          safe to touch
        </span>{' '}
        — before you touch it.
      </h1>
      <p className="relative mt-4 max-w-xl text-text-dim sm:text-lg">
        IssueMatch AI matches you to open-source issues you can actually
        handle, and proves it with static analysis — not a guess, not an LLM.
      </p>
      <div className="relative mt-8 flex flex-wrap items-center justify-center gap-3">
        <button
          type="button"
          onClick={loginWithGitHub}
          className="rounded-lg bg-accent px-6 py-3 text-sm font-semibold text-on-accent shadow-lg shadow-accent/20 transition-colors hover:bg-accent-bright"
        >
          Sign in with GitHub
        </button>
        <Link
          to="/how-it-works"
          className="rounded-lg border border-border-bright px-6 py-3 text-sm font-medium text-text-bright transition-colors hover:bg-surface-2"
        >
          View Technical Docs
        </Link>
      </div>

      {/* Terminal mockup — illustrative demo of the analyze flow, not a live feed */}
      <div className="relative mt-10 w-full overflow-hidden rounded-xl border border-border bg-surface-0 text-left shadow-2xl shadow-black/50">
        <div className="flex items-center gap-2 border-b border-border bg-surface-1 px-4 py-2.5">
          <span className="h-3 w-3 rounded-full bg-[#FF5F56]" />
          <span className="h-3 w-3 rounded-full bg-[#FFBD2E]" />
          <span className="h-3 w-3 rounded-full bg-[#27C93F]" />
          <span className="metric ml-2 text-xs text-text-dim">
            issuematch-engine
          </span>
        </div>
        <div className="metric overflow-x-auto p-5 text-xs leading-loose text-text-dim">
          <div className="text-cyan">
            ➜ <span className="text-accent-bright">analyze</span>{' '}
            target_repository=&quot;vercel/next.js&quot;
          </div>
          <div>[INFO] Establishing local sentence embeddings...</div>
          <div>[INFO] Parsing AST with tree-sitter...</div>
          <div>[INFO] Calculating call-graph fan-in...</div>
          <div className="mt-1.5 text-cyan">
            ➜ <span className="text-accent-bright">match_results</span>
          </div>
          <div className="mt-0.5 flex justify-between border-b border-border/60 pb-1">
            <span className="text-text-bright">
              Issue #4219: Improve caching logic
            </span>
            <span className="text-violet">Confidence: 94%</span>
          </div>
          <div className="mt-1 flex flex-wrap gap-4 border-l-2 border-border/60 pl-3">
            <span>
              Fan-in: <span className="text-cyan">Low (12)</span>
            </span>
            <span>
              Complexity: <span className="text-cyan">O(n)</span>
            </span>
            <span>
              Churn: <span className="text-accent-bright">Stable</span>
            </span>
          </div>
        </div>
      </div>

      <section className="relative mt-16 w-full text-left">
        <h2 className="mb-6 text-xl font-bold text-text-bright">
          System Architecture
        </h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="flex flex-col gap-2 rounded-xl border border-border bg-surface-1/60 p-5 backdrop-blur-md transition-colors hover:border-accent/40"
            >
              <span className={`metric text-xs ${f.eyebrowColor}`}>
                {f.eyebrow}
              </span>
              <h3 className="text-lg font-semibold text-text-bright">
                {f.title}
              </h3>
              <p className="mt-1 text-sm text-text-dim">{f.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
