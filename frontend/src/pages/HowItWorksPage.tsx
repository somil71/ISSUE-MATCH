import { Link } from 'react-router-dom'
import { GaugeIcon, RouteIcon, ShieldIcon, TargetIcon } from '../components/Icons'

const SIGNALS = [
  {
    name: 'Fan-in',
    detail:
      'How many other places call it, resolved by name. Ambiguous names are flagged, never guessed.',
  },
  {
    name: 'Complexity',
    detail:
      'Independent decision paths through the function — branches, loops, boolean operators — counted from the tree.',
  },
  {
    name: 'Test proximity',
    detail:
      'Whether a recognized test file references this function by name anywhere in the repo.',
  },
  {
    name: 'Git churn',
    detail:
      'How often, and how recently, the file changed — from one pass over git log, not a call per file.',
  },
]

const STEPS = [
  {
    icon: <TargetIcon className="h-4.5 w-4.5" />,
    accent: 'violet' as const,
    title: 'Parsing the code',
    tagline: 'Real tree-sitter ASTs, not regex or an LLM reading the file.',
    body: (
      <>
        <p className="text-sm text-text-dim">
          Every Python, JavaScript, TypeScript, and TSX file is parsed into a
          real abstract syntax tree. From that tree, four signals are
          measured per function:
        </p>
        <dl className="mt-4 grid gap-3 sm:grid-cols-2">
          {SIGNALS.map((s) => (
            <div key={s.name} className="rounded-lg border border-border bg-surface-0 p-3">
              <dt className="metric text-xs font-semibold text-text-bright">
                {s.name}
              </dt>
              <dd className="mt-1 text-xs leading-relaxed text-text-dim">
                {s.detail}
              </dd>
            </div>
          ))}
        </dl>
      </>
    ),
  },
  {
    icon: <GaugeIcon className="h-4.5 w-4.5" />,
    accent: 'cyan' as const,
    title: 'The Blast Radius Score',
    tagline: 'One transparent formula, the same weights for every repo.',
    body: (
      <>
        <div className="metric overflow-x-auto rounded-lg border border-border bg-surface-0 p-4 text-sm">
          <span className="text-text-bright">score</span>
          <span className="text-text-dim"> = </span>
          <span className="text-violet">0.35</span>
          <span className="text-text-dim">×fan-in + </span>
          <span className="text-cyan">0.30</span>
          <span className="text-text-dim">×complexity + </span>
          <span className="text-accent-bright">0.20</span>
          <span className="text-text-dim">×(no test?1:0) + </span>
          <span className="text-safe">0.15</span>
          <span className="text-text-dim">×churn</span>
        </div>
        <p className="mt-4 text-sm text-text-dim">
          Each term is normalized against the rest of the repo first, so the
          score means "risky relative to this codebase," not an arbitrary
          absolute number. Below the threshold, a function is bucketed{' '}
          <span className="font-medium text-safe">Start Here</span>; above
          it, <span className="font-medium text-danger">Here Be Dragons</span>.
          The risk tolerance slider only moves that threshold — it never
          touches the formula or its weights.
        </p>
      </>
    ),
  },
  {
    icon: <RouteIcon className="h-4.5 w-4.5" />,
    accent: 'accent' as const,
    title: 'Matching you to issues',
    tagline: 'Local embeddings, not a hosted AI API.',
    body: (
      <p className="text-sm text-text-dim">
        A small sentence-transformer model (
        <code className="metric rounded bg-surface-0 px-1.5 py-0.5 text-xs text-text-bright">
          all-MiniLM-L6-v2
        </code>
        ) runs entirely on this server's CPU to turn your skills and each
        issue's text into vectors, compared by cosine similarity. The
        overlapping terms shown under each match come from TF-IDF, a plain
        word-weighting statistic — an independently computed second signal,
        not the model explaining itself. Explanations of what an issue is
        about, and the auto-drafted "I'd like to work on this" comment, are
        built the same way: a deterministic template filled in with facts
        already computed (a parsed sentence structure, a real blast-radius
        summary, a real git commit author) — never free-generated text.
      </p>
    ),
  },
  {
    icon: <ShieldIcon className="h-4.5 w-4.5" />,
    accent: 'violet' as const,
    title: 'The zero-LLM guarantee',
    tagline: 'Enforced structurally, not just claimed.',
    body: (
      <>
        <p className="text-sm text-text-dim">
          Every outbound network call this backend makes is routed through
          one function that logs the destination host before the request
          goes out. The Trust Panel in the header shows that live log — if
          this tool ever contacted anything other than{' '}
          <code className="metric rounded bg-surface-0 px-1.5 py-0.5 text-xs text-text-bright">
            api.github.com
          </code>
          , you'd see it turn red in real time, not after the fact.
        </p>
        <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-safe/30 bg-safe-bg px-3 py-1.5">
          <ShieldIcon className="h-3.5 w-3.5 text-safe" />
          <span className="metric text-xs text-safe">
            api.github.com only
          </span>
        </div>
      </>
    ),
  },
]

const ACCENT_TEXT: Record<'violet' | 'cyan' | 'accent', string> = {
  violet: 'text-violet',
  cyan: 'text-cyan',
  accent: 'text-accent-bright',
}
const ACCENT_BG: Record<'violet' | 'cyan' | 'accent', string> = {
  violet: 'bg-violet-bg',
  cyan: 'bg-cyan-bg',
  accent: 'bg-accent-bg',
}

export function HowItWorksPage() {
  return (
    <>
      <div className="mx-auto max-w-2xl text-center">
        <div className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-1 px-3 py-1">
          <ShieldIcon className="h-3.5 w-3.5 text-cyan" />
          <span className="metric text-xs uppercase tracking-widest text-text-dim">
            The zero-LLM promise
          </span>
        </div>
        <h1 className="mt-4 text-4xl font-bold tracking-tight text-text-bright">
          Deterministic methodology.
          <br />
          <span className="text-accent-bright">Calculated certainty.</span>
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-sm leading-relaxed text-text-dim">
          Every number this tool shows you is either a formula you can see or
          a fact read straight from git — never a model's guess. Here's
          exactly what runs, in order, when you analyze a repo.
        </p>
      </div>

      <div className="relative mt-14 flex flex-col gap-10">
        <div
          aria-hidden
          className="absolute left-[19px] top-3 hidden h-[calc(100%-2.5rem)] w-px bg-border sm:block"
        />
        {STEPS.map((step, i) => (
          <div key={step.title} className="relative flex gap-5">
            <div className="relative z-10 hidden shrink-0 sm:block">
              <div className="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface-1">
                <span className="metric text-sm font-semibold text-text-bright">
                  {i + 1}
                </span>
              </div>
            </div>
            <div className="min-w-0 flex-1 rounded-xl border border-border bg-surface-1 p-6">
              <div className="flex items-start gap-3">
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${ACCENT_BG[step.accent]} ${ACCENT_TEXT[step.accent]}`}
                >
                  {step.icon}
                </div>
                <div className="min-w-0">
                  <h2 className="text-lg font-semibold text-text-bright">
                    {step.title}
                  </h2>
                  <p className="mt-0.5 text-sm text-text-dim">
                    {step.tagline}
                  </p>
                </div>
              </div>
              <div className="mt-4">{step.body}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-10 flex justify-center">
        <Link
          to="/"
          className="rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-on-accent transition-colors hover:bg-accent-bright"
        >
          Back to the workspace
        </Link>
      </div>
    </>
  )
}
