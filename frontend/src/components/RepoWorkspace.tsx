import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  ApiError,
  apiGet,
  apiPostJson,
  type CurrentUser,
  type FunctionMetric,
  type LabelAccuracy,
  type PrPlaybook,
  type RankedIssuesResponse,
  type RepoAnalysis,
} from '../lib/api'
import { useToast } from '../lib/toast'
import { BlastRadiusMap } from './BlastRadiusMap'
import { GaugeIcon, LandmarkIcon, RouteIcon, SparklesIcon, TargetIcon } from './Icons'
import { SectionCard } from './SectionCard'
import { AnalyzeResultsSkeleton, IssueListSkeleton } from './Skeleton'
import { SkillProfile } from './SkillProfile'

function parseOwnerRepo(input: string): [string, string] | null {
  let cleaned = input.trim()
  cleaned = cleaned.replace(/^https?:\/\//, '').replace(/^github\.com\//, '')
  cleaned = cleaned.replace(/\.git$/, '').replace(/\/+$/, '')
  const parts = cleaned.split('/').filter(Boolean)
  if (parts.length < 2) return null
  return [parts[0], parts[1]]
}

/** Lets a user shift the Start Here / Here Be Dragons boundary themselves
 * instead of accepting one fixed global cutoff — the formula and its
 * weights never change, only where the line falls on the same score. */
function computeBucket(
  score: number,
  threshold: number,
): 'start_here' | 'here_be_dragons' {
  return score < threshold ? 'start_here' : 'here_be_dragons'
}

function BucketBadge({ bucket }: { bucket: 'start_here' | 'here_be_dragons' }) {
  if (bucket === 'start_here') {
    return (
      <span className="whitespace-nowrap rounded-full bg-safe-bg px-2 py-0.5 text-xs font-medium text-safe">
        Start Here
      </span>
    )
  }
  return (
    <span className="whitespace-nowrap rounded-full bg-danger-bg px-2 py-0.5 text-xs font-medium text-danger">
      Here Be Dragons
    </span>
  )
}

function severityColor(value: number): string {
  if (value < 0.34) return 'bg-safe'
  if (value < 0.67) return 'bg-caution'
  return 'bg-danger'
}

function SignalBar({
  label,
  value,
  raw,
}: {
  label: string
  value: number
  raw: string | number
}) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100)
  return (
    <div
      className="flex items-center gap-1.5"
      title={`${label}: ${pct}% of this repo's range`}
    >
      <span className="w-9 shrink-0 text-xs text-text-dim">{label}</span>
      <div className="h-1.5 w-16 shrink-0 overflow-hidden rounded-full bg-surface-3">
        <div
          className={`h-full rounded-full ${severityColor(value)}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="metric w-8 shrink-0 text-right text-xs text-text-dim">
        {raw}
      </span>
    </div>
  )
}

function SignalBars({ fn }: { fn: FunctionMetric }) {
  return (
    <div className="flex flex-col gap-1 py-0.5">
      <SignalBar label="fan-in" value={fn.normalized_fan_in} raw={fn.fan_in} />
      <SignalBar
        label="complex"
        value={fn.normalized_complexity}
        raw={fn.cyclomatic_complexity}
      />
      <SignalBar
        label="churn"
        value={fn.normalized_churn}
        raw={fn.churn_intensity.toFixed(2)}
      />
    </div>
  )
}

function BucketSummary({
  functions,
  threshold,
}: {
  functions: FunctionMetric[]
  threshold: number
}) {
  const startHere = functions.filter(
    (f) => computeBucket(f.blast_radius_score, threshold) === 'start_here',
  ).length
  const dragons = functions.length - startHere
  return (
    <>
      <span className="text-safe">{startHere} Start Here</span>
      {' · '}
      <span className="text-danger">{dragons} Here Be Dragons</span>
    </>
  )
}

type BucketFilter = 'all' | 'start_here' | 'here_be_dragons'

const BUCKET_FILTERS: { key: BucketFilter; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'start_here', label: 'Start Here' },
  { key: 'here_be_dragons', label: 'Here Be Dragons' },
]

function ReadinessGauge({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(1, score))
  const radius = 42
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - pct)

  return (
    <div className="relative flex h-32 w-32 shrink-0 items-center justify-center">
      <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="var(--color-surface-3)"
          strokeWidth="8"
        />
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="var(--color-accent-bright)"
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </svg>
      <div className="metric absolute text-3xl font-bold text-text-bright">
        {Math.round(pct * 100)}%
      </div>
    </div>
  )
}

function ReadinessCard({ analysis }: { analysis: RepoAnalysis }) {
  const { skill_gap, readiness_score, avg_blast_radius_score } = analysis
  const skillOverlapRatio =
    skill_gap.required.length > 0
      ? skill_gap.have.length / skill_gap.required.length
      : 1
  const gapPenalty = 1 / (1 + skill_gap.gap.length)

  return (
    <SectionCard
      icon={<GaugeIcon />}
      title="Your readiness for this repo"
      description="Repo-level, not per-issue — real issue text rarely names the exact files it touches, so this compares your skills against the repo's actual dependency manifests instead of guessing."
      accent="violet"
    >
      <div className="flex flex-col items-center gap-4">
        <ReadinessGauge score={readiness_score} />
        <p className="metric text-center text-xs text-text-dim">
          0.40 × {skillOverlapRatio.toFixed(2)} (skill overlap) + 0.35 ×{' '}
          {(1 - avg_blast_radius_score).toFixed(2)} (1 − avg blast radius)
          {' + '}
          0.25 × {gapPenalty.toFixed(2)} (gap penalty)
        </p>
        <div className="w-full">
          <div className="metric flex flex-col gap-1.5 text-sm">
            <div className="flex justify-between border-b border-border pb-1.5">
              <span className="text-text-dim">Required</span>
              <span className="text-text-bright">
                {skill_gap.required.join(', ') || 'none'}
              </span>
            </div>
            <div className="flex justify-between border-b border-border pb-1.5">
              <span className="text-text-dim">You have</span>
              <span className="text-accent-bright">
                {skill_gap.have.join(', ') || 'none'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-dim">Gap</span>
              <span className="text-danger">
                {skill_gap.gap.join(', ') || 'none'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </SectionCard>
  )
}

function FirstMergePath({
  functions,
  threshold,
}: {
  functions: FunctionMetric[]
  threshold: number
}) {
  const path = useMemo(() => {
    return functions
      .filter((fn) => computeBucket(fn.blast_radius_score, threshold) === 'start_here')
      .sort((a, b) => a.blast_radius_score - b.blast_radius_score)
      .slice(0, 3)
  }, [functions, threshold])

  if (path.length === 0) {
    return (
      <p className="text-sm text-text-dim">
        No functions fall under "Start Here" at this risk tolerance — try
        loosening the slider above the table.
      </p>
    )
  }

  return (
    <ol className="flex flex-col gap-3">
      {path.map((fn, i) => (
        <li
          key={fn.id}
          className="flex gap-3 rounded-lg border border-border p-3"
        >
          <span className="metric flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-safe-bg text-xs font-semibold text-safe">
            {i + 1}
          </span>
          <div>
            <p className="metric text-sm text-text-bright">
              {fn.name}{' '}
              <span className="text-text-dim">
                — {fn.file}:{fn.start_line}
              </span>
            </p>
            <p className="mt-1 text-xs text-text-dim">{fn.summary}</p>
          </div>
        </li>
      ))}
    </ol>
  )
}

function CodebaseLandmarks({ functions }: { functions: FunctionMetric[] }) {
  const landmarks = useMemo(
    () => [...functions].sort((a, b) => b.fan_in - a.fan_in).slice(0, 5),
    [functions],
  )

  return (
    <ul className="flex flex-col gap-1.5">
      {landmarks.map((fn) => (
        <li
          key={fn.id}
          className="flex items-center justify-between gap-3 rounded bg-surface-2 px-3 py-2 transition-colors hover:border-accent/40"
        >
          <span className="metric truncate text-sm text-accent-bright">
            {fn.name}
          </span>
          <span className="metric shrink-0 rounded bg-surface-3 px-1.5 py-0.5 text-xs text-text-dim">
            {fn.fan_in} callers
          </span>
        </li>
      ))}
    </ul>
  )
}

function LabelAccuracyScoreboard({ accuracy }: { accuracy: LabelAccuracy }) {
  if (accuracy.github_labeled_count === 0) return null

  return (
    <div className="mb-4 rounded-lg border border-border bg-surface-0 p-3">
      <p className="text-xs text-text-dim">
        GitHub labels{' '}
        <span className="metric text-text-bright">
          {accuracy.github_labeled_count}
        </span>{' '}
        issue{accuracy.github_labeled_count === 1 ? '' : 's'} here as
        beginner-friendly.
        {accuracy.verified_count > 0 ? (
          <>
            {' '}
            Our engine checked the actual code named in{' '}
            <span className="metric text-text-bright">
              {accuracy.verified_count}
            </span>{' '}
            of them
            {accuracy.disagreement_count > 0 ? (
              <>
                , and found{' '}
                <span className="metric font-medium text-danger">
                  {accuracy.disagreement_count}
                </span>{' '}
                quietly touching high-risk code anyway.
              </>
            ) : (
              ' — every one checked out as genuinely low-risk.'
            )}
          </>
        ) : (
          ' None of them explicitly name a function or file we could verify against.'
        )}
      </p>
      {accuracy.disagreements.length > 0 && (
        <ul className="mt-2 flex flex-col gap-1">
          {accuracy.disagreements.map((d) => (
            <li key={d.number} className="text-xs">
              <a
                href={d.url}
                target="_blank"
                rel="noreferrer"
                className="text-danger hover:underline"
              >
                #{d.number} {d.title}
              </a>
              <span className="metric ml-2 text-text-dim">
                touches {d.risky_reference.name ?? d.risky_reference.file}{' '}
                (Here Be Dragons)
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function CopyButton({ text, label = 'Copy to clipboard' }: { text: string; label?: string }) {
  const toast = useToast()

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    toast.push('Copied to clipboard.', 'success')
  }

  return (
    <button
      type="button"
      onClick={handleCopy}
      className="rounded-full bg-surface-2 px-2.5 py-1 text-xs font-medium text-text-dim transition-colors hover:bg-accent-bg hover:text-accent-bright"
    >
      {label}
    </button>
  )
}

function ContributorPlaybookPanel({
  draft,
  playbook,
}: {
  draft: string
  playbook: PrPlaybook
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="text-xs font-medium text-accent-bright hover:underline"
      >
        {expanded ? 'Hide contributor playbook' : "Draft my \"I'd like to work on this\" comment"}
      </button>
      {expanded && (
        <div className="mt-1.5 flex flex-col gap-3 rounded-md border border-border bg-surface-0 p-2.5">
          <div>
            <p className="whitespace-pre-wrap text-xs text-text-dim">{draft}</p>
            <div className="mt-2">
              <CopyButton text={draft} />
            </div>
          </div>

          <div className="border-t border-border pt-3">
            <span className="text-xs font-semibold text-text-bright">
              Next: from claimed issue to opened PR
            </span>

            <div className="mt-2 flex flex-wrap items-center gap-2">
              <span className="text-xs text-text-dim">Suggested branch:</span>
              <code className="metric rounded bg-surface-2 px-1.5 py-0.5 text-xs text-text-bright">
                {playbook.branch_name}
              </code>
              <CopyButton text={playbook.branch_name} label="Copy" />
            </div>

            {playbook.start_here && (
              <p className="mt-2 text-xs text-text-dim">
                Start at{' '}
                <span className="metric text-text-bright">
                  {playbook.start_here.function}
                </span>{' '}
                in{' '}
                <span className="metric text-text-bright">{playbook.start_here.file}</span>.
                {playbook.start_here.direct_callers.length > 0 && (
                  <>
                    {' '}
                    Called directly by:{' '}
                    <span className="metric text-text-bright">
                      {playbook.start_here.direct_callers.join(', ')}
                    </span>
                    .
                  </>
                )}
              </p>
            )}

            <p className="mt-2 text-xs text-text-dim">{playbook.test_guidance}</p>

            <div className="mt-2 rounded-md border border-border bg-surface-1 p-2">
              <p className="whitespace-pre-wrap text-xs text-text-dim">
                {playbook.pr_description}
              </p>
              <div className="mt-2">
                <CopyButton text={playbook.pr_description} label="Copy PR description" />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export function RepoWorkspace({ user }: { user: CurrentUser }) {
  const [repoInput, setRepoInput] = useState('')
  const [search, setSearch] = useState('')
  const [bucketFilter, setBucketFilter] = useState<BucketFilter>('all')
  const [bucketThreshold, setBucketThreshold] = useState(0.5)
  const [activeRepo, setActiveRepo] = useState<[string, string] | null>(null)
  const [mapFunctionId, setMapFunctionId] = useState<string | null>(null)
  const tableScrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    tableScrollRef.current?.scrollTo({ top: 0 })
  }, [search, bucketFilter])

  const analysis = useMutation({
    mutationFn: ([owner, name]: [string, string]) =>
      apiPostJson<RepoAnalysis>(`/repos/${owner}/${name}/analyze`),
  })

  const issues = useMutation({
    mutationFn: ([owner, name]: [string, string]) =>
      apiGet<RankedIssuesResponse>(`/repos/${owner}/${name}/issues`),
  })

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    const parsed = parseOwnerRepo(repoInput)
    if (!parsed) return
    setActiveRepo(parsed)
    // Analyze first and await it so the backend's per-repo cache is warm
    // before /issues runs — that cache is what lets an issue's text be
    // cross-referenced against real function-level blast radius data.
    await analysis.mutateAsync(parsed).catch(() => undefined)
    issues.mutate(parsed)
  }

  const filteredFunctions = useMemo(() => {
    const functions = analysis.data?.functions ?? []
    const term = search.trim().toLowerCase()
    return functions.filter((fn) => {
      if (
        bucketFilter !== 'all' &&
        computeBucket(fn.blast_radius_score, bucketThreshold) !== bucketFilter
      ) {
        return false
      }
      if (
        term &&
        !fn.name.toLowerCase().includes(term) &&
        !fn.file.toLowerCase().includes(term)
      ) {
        return false
      }
      return true
    })
  }, [analysis.data, search, bucketFilter, bucketThreshold])

  return (
    <>
      <div className="grid gap-0 sm:grid-cols-2 sm:items-start sm:gap-x-6">
      <SkillProfile user={user} />
      <SectionCard
        icon={<TargetIcon />}
        title="Blast Radius Engine — analyze a repo"
        description="Real tree-sitter parse + call graph + cyclomatic complexity + test proximity + git churn, computed live. No AI, no external API — just the repo you name."
        accent="cyan"
      >
        <form onSubmit={handleSubmit}>
          <div className="flex items-center gap-2 rounded-lg border border-border bg-surface-0 px-3 py-2.5 transition-colors focus-within:border-accent">
            <svg
              viewBox="0 0 16 16"
              className="h-4 w-4 shrink-0 text-text-dim"
              fill="currentColor"
            >
              <path d="M8 0a8 8 0 0 0-2.53 15.59c.4.07.55-.17.55-.38l-.01-1.49c-2.23.48-2.7-1.07-2.7-1.07-.36-.93-.89-1.17-.89-1.17-.72-.5.06-.49.06-.49.8.06 1.22.82 1.22.82.71 1.22 1.87.87 2.33.66.07-.52.28-.87.5-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.14-.08-.2-.36-1.01.08-2.12 0 0 .67-.21 2.2.82a7.5 7.5 0 0 1 4 0c1.53-1.03 2.2-.82 2.2-.82.44 1.11.16 1.92.08 2.12.51.55.82 1.27.82 2.14 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48l-.01 2.2c0 .21.15.46.55.38A8 8 0 0 0 8 0Z" />
            </svg>
            <input
              type="text"
              value={repoInput}
              onChange={(e) => setRepoInput(e.target.value)}
              placeholder="owner/repo, e.g. pallets/itsdangerous"
              className="metric flex-1 bg-transparent text-sm text-text-bright placeholder:text-text-dim focus:outline-none"
            />
            <button
              type="submit"
              disabled={analysis.isPending}
              className="shrink-0 rounded-md bg-accent px-4 py-1.5 text-sm font-medium text-on-accent transition-colors hover:bg-accent-bright disabled:opacity-50"
            >
              {analysis.isPending ? 'Analyzing…' : 'Analyze'}
            </button>
          </div>
        </form>

        {analysis.isPending && (
          <>
            <p className="mt-4 text-sm text-text-dim">
              Cloning, parsing every source file, walking git history, and
              building the call graph — first-time analysis of a repo can
              take a little while.
            </p>
            <AnalyzeResultsSkeleton />
          </>
        )}

        {analysis.isError && (
          <p className="mt-4 text-sm text-danger">
            {analysis.error instanceof ApiError
              ? analysis.error.message
              : 'Analysis failed.'}
          </p>
        )}

        {analysis.isSuccess && (
          <div className="mt-4">
            <div className="metric rounded-md border border-border bg-surface-2 p-3 text-xs">
              <p className="text-text-dim">
                {analysis.data.repo} @{' '}
                <span className="text-accent-bright">
                  {analysis.data.commit_sha.slice(0, 7)}
                </span>{' '}
                — {analysis.data.file_count} files, {analysis.data.function_count}{' '}
                functions
              </p>
              <p className="mt-1.5 text-sm">
                <BucketSummary
                  functions={analysis.data.functions}
                  threshold={bucketThreshold}
                />
              </p>
            </div>

            <div className="mt-4">
              <label className="metric flex justify-between text-xs text-text-dim">
                <span>Risk tolerance</span>
                <span className="text-accent-bright">
                  {bucketThreshold < 0.35
                    ? 'Cautious'
                    : bucketThreshold > 0.65
                      ? 'Adventurous'
                      : 'Balanced'}
                </span>
              </label>
              <input
                type="range"
                min={0.15}
                max={0.85}
                step={0.05}
                value={bucketThreshold}
                onChange={(e) => setBucketThreshold(Number(e.target.value))}
                className="mt-1.5 h-1.5 w-full accent-accent"
              />
              <div className="metric mt-1 flex justify-between text-xs text-text-dim">
                <span>Cautious</span>
                <span>Balanced</span>
                <span>Adventurous</span>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-2">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter by function or file…"
                className="metric rounded-md border border-border bg-surface-0 px-3 py-1.5 text-xs text-text-bright placeholder:text-text-dim focus:border-accent focus:outline-none"
              />
              <div className="flex gap-1.5">
                {BUCKET_FILTERS.map(({ key, label }) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setBucketFilter(key)}
                    className={`rounded-full px-2.5 py-1 text-xs font-medium transition-colors ${
                      bucketFilter === key
                        ? 'bg-accent text-white'
                        : 'bg-surface-2 text-text-dim hover:text-text-bright'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <span className="metric text-xs font-medium text-text-bright">
                {filteredFunctions.length}{' '}
                <span className="font-normal text-text-dim">
                  of {analysis.data?.functions.length ?? 0} shown
                </span>
              </span>
            </div>

            <div
              ref={tableScrollRef}
              className="mt-3 max-h-[32rem] overflow-x-auto overflow-y-auto rounded-md border border-border"
            >
              <table className="w-full table-fixed text-left text-sm">
                <thead className="sticky top-0 bg-surface-2 text-text-dim">
                  <tr>
                    <th className="w-40 px-3 py-2 font-medium">Function</th>
                    <th className="w-52 px-3 py-2 font-medium">File</th>
                    <th className="w-48 px-3 py-2 font-medium">Signals</th>
                    <th className="w-16 px-3 py-2 font-medium text-right">Test</th>
                    <th className="w-28 px-3 py-2 font-medium">Bucket</th>
                    <th className="px-3 py-2 font-medium">Why</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFunctions.map((fn) => (
                    <tr
                      key={fn.id}
                      className="border-t border-border align-top transition-colors hover:bg-surface-2/50"
                    >
                      <td className="metric w-40 truncate px-3 py-2 text-text-bright">
                        <button
                          type="button"
                          onClick={() => setMapFunctionId(fn.id)}
                          className="max-w-full truncate align-bottom hover:text-accent-bright hover:underline"
                          title={`${fn.name} — ${fn.transitive_fan_in} functions transitively depend on this — click to trace the real call graph outward`}
                        >
                          {fn.name}
                        </button>
                        {fn.name_is_ambiguous && (
                          <span className="ml-1 text-xs text-caution">
                            (ambiguous)
                          </span>
                        )}
                      </td>
                      <td
                        className="metric w-52 truncate px-3 py-2 text-text-dim"
                        title={`${fn.file}:${fn.start_line}`}
                      >
                        {fn.file}:{fn.start_line}
                      </td>
                      <td className="w-48 px-3 py-2">
                        <SignalBars fn={fn} />
                      </td>
                      <td className="metric w-16 px-3 py-2 text-right">
                        {fn.has_test_coverage ? (
                          <span className="text-safe">yes</span>
                        ) : (
                          <span className="text-text-dim">no</span>
                        )}
                      </td>
                      <td className="w-28 px-3 py-2">
                        <BucketBadge
                          bucket={computeBucket(fn.blast_radius_score, bucketThreshold)}
                        />
                      </td>
                      <td
                        className="line-clamp-2 px-3 py-2 text-xs text-text-dim"
                        title={fn.summary}
                      >
                        {fn.summary}
                      </td>
                    </tr>
                  ))}
                  {filteredFunctions.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-3 py-6 text-center text-text-dim">
                        No functions match your filter.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </SectionCard>
      </div>

      {analysis.isSuccess && (
        <SectionCard
          icon={<RouteIcon />}
          title="Your first merge path"
          description="The 3 safest Start Here functions in this repo, ordered easiest to hardest — a suggested on-ramp, not a mandate. Respects the risk tolerance slider above."
          accent="cyan"
        >
          <FirstMergePath
            functions={analysis.data.functions}
            threshold={bucketThreshold}
          />
        </SectionCard>
      )}

      {analysis.isSuccess && (
        <SectionCard
          icon={<LandmarkIcon />}
          title="Codebase landmarks"
          description="The most depended-on functions in this repo, by fan-in — touch these last, and only with tests running."
          accent="none"
        >
          <CodebaseLandmarks functions={analysis.data.functions} />
        </SectionCard>
      )}

      {analysis.isSuccess && <ReadinessCard analysis={analysis.data} />}

      <SectionCard
        icon={<SparklesIcon />}
        title="Recommended issues"
        description="Local sentence embeddings rank open issues against your skill profile — overlapping terms shown are TF-IDF weighted, not a bare similarity float."
        accent="accent"
      >

        {issues.isPending && (
          <>
            <p className="mt-4 text-sm text-text-dim">Ranking open issues…</p>
            <IssueListSkeleton />
          </>
        )}
        {issues.isError && (
          <p className="mt-4 text-sm text-danger">
            {issues.error instanceof ApiError
              ? issues.error.message
              : 'Could not load issues.'}
          </p>
        )}
        {issues.isSuccess && (
          <div className="mt-4">
            <p className="text-sm text-text-dim">
              Your skills:{' '}
              <span className="metric text-text-bright">
                {issues.data.user_skills.join(', ') || 'none set'}
              </span>
              {issues.data.inferred_skills.length > 0 && (
                <>
                  {' '}
                  · GitHub-inferred:{' '}
                  <span className="metric text-text-bright">
                    {issues.data.inferred_skills.join(', ')}
                  </span>
                </>
              )}
            </p>
            <div className="mt-3">
              <LabelAccuracyScoreboard accuracy={issues.data.label_accuracy} />
            </div>
            <ul className="flex flex-col gap-3">
              {issues.data.issues.map((issue) => (
                <li
                  key={issue.number}
                  className="rounded-lg border border-border p-4 transition-colors hover:border-border-bright"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <a
                        href={issue.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm font-medium text-text-bright hover:text-accent-bright hover:underline"
                      >
                        #{issue.number} {issue.title}
                      </a>
                      {issue.beginner_friendly_label && (
                        <span
                          className="whitespace-nowrap rounded-full bg-safe-bg px-2 py-0.5 text-xs font-medium text-safe"
                          title="GitHub carries a beginner-friendly label (good first issue / help wanted / etc.) on this issue"
                        >
                          GitHub: beginner-friendly
                        </span>
                      )}
                    </div>
                    <span className="metric shrink-0 text-xs text-text-dim">
                      similarity {issue.similarity.toFixed(3)}
                    </span>
                  </div>
                  {issue.labels.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {issue.labels.map((label) => (
                        <span
                          key={label.name}
                          className="rounded-full border px-2 py-0.5 text-xs"
                          style={{
                            borderColor: `#${label.color}`,
                            color: `#${label.color}`,
                          }}
                        >
                          {label.name}
                        </span>
                      ))}
                    </div>
                  )}
                  <p className="mt-2 text-xs text-text-dim">
                    {issue.explanation}
                  </p>
                  {issue.overlapping_terms.length > 0 && (
                    <p className="mt-1 text-xs text-text-dim">
                      matched on:{' '}
                      <span className="metric text-text-bright">
                        {issue.overlapping_terms.join(', ')}
                      </span>
                    </p>
                  )}
                  {issue.code_references.length > 0 && (
                    <div className="mt-2 flex flex-col gap-1 rounded-md border border-border bg-surface-0 p-2">
                      <span className="text-xs text-text-dim">
                        Our engine's take on the code this issue names:
                      </span>
                      {issue.code_references.map((ref, i) => (
                        <div
                          key={i}
                          className="metric flex items-center justify-between gap-2 text-xs"
                        >
                          <span className="text-text-bright">
                            {ref.name ?? ref.file}
                          </span>
                          {ref.bucket && <BucketBadge bucket={ref.bucket} />}
                        </div>
                      ))}
                    </div>
                  )}
                  <ContributorPlaybookPanel
                    draft={issue.draft_comment}
                    playbook={issue.pr_playbook}
                  />
                </li>
              ))}
            </ul>
            {issues.data.issues.length > 0 && !issues.data.analyzed && (
              <p className="mt-2 text-xs text-text-dim">
                Code-level cross-references need the repo analyzed first —
                run Analyze above to see them.
              </p>
            )}
            {issues.data.issues.length === 0 && (
              <p className="text-sm text-text-dim">
                This repo has no open issues right now — try another repo to
                see ranked recommendations.
              </p>
            )}
          </div>
        )}
      </SectionCard>

      {mapFunctionId && activeRepo && (
        <BlastRadiusMap
          owner={activeRepo[0]}
          name={activeRepo[1]}
          functionId={mapFunctionId}
          onClose={() => setMapFunctionId(null)}
        />
      )}
    </>
  )
}
