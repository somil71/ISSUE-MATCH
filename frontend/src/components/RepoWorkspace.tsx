import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  ApiError,
  apiGet,
  apiPostJson,
  type FunctionMetric,
  type RankedIssuesResponse,
  type RepoAnalysis,
} from '../lib/api'

function SkillChips({
  skills,
  tone,
}: {
  skills: string[]
  tone: 'neutral' | 'safe' | 'danger'
}) {
  const toneClass =
    tone === 'safe'
      ? 'bg-safe-bg text-safe'
      : tone === 'danger'
        ? 'bg-danger-bg text-danger'
        : 'bg-surface-2 text-text-bright'
  if (skills.length === 0) {
    return <span className="text-xs text-text-dim">none</span>
  }
  return (
    <div className="flex flex-wrap gap-1.5">
      {skills.map((s) => (
        <span
          key={s}
          className={`metric rounded-full px-2 py-0.5 text-xs ${toneClass}`}
        >
          {s}
        </span>
      ))}
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
    <section className="mt-6 rounded-lg border border-border bg-surface-1 p-6">
      <h2 className="text-sm font-medium text-text-bright">
        Your readiness for this repo
      </h2>
      <p className="mt-1 text-sm text-text-dim">
        Repo-level, not per-issue — real issue text rarely names the exact
        files it touches, so this compares your skills against the repo's
        actual dependency manifests instead of guessing.
      </p>

      <div className="mt-4 flex flex-col gap-2">
        <div>
          <span className="text-xs text-text-dim">Required (from manifests)</span>
          <div className="mt-1">
            <SkillChips skills={skill_gap.required} tone="neutral" />
          </div>
        </div>
        <div>
          <span className="text-xs text-text-dim">You have</span>
          <div className="mt-1">
            <SkillChips skills={skill_gap.have} tone="safe" />
          </div>
        </div>
        <div>
          <span className="text-xs text-text-dim">Gap</span>
          <div className="mt-1">
            <SkillChips skills={skill_gap.gap} tone="danger" />
          </div>
        </div>
      </div>

      <div className="mt-6 border-t border-border pt-4">
        <div className="metric text-3xl font-semibold text-text-bright">
          {Math.round(readiness_score * 100)}
          <span className="text-base text-text-dim">/100</span>
        </div>
        <p className="metric mt-1 text-xs text-text-dim">
          0.40 × {skillOverlapRatio.toFixed(2)} (skill overlap) + 0.35 ×{' '}
          {(1 - avg_blast_radius_score).toFixed(2)} (1 − avg blast radius) +
          0.25 × {gapPenalty.toFixed(2)} (gap penalty)
        </p>
      </div>
    </section>
  )
}

function parseOwnerRepo(input: string): [string, string] | null {
  let cleaned = input.trim()
  cleaned = cleaned.replace(/^https?:\/\//, '').replace(/^github\.com\//, '')
  cleaned = cleaned.replace(/\.git$/, '').replace(/\/+$/, '')
  const parts = cleaned.split('/').filter(Boolean)
  if (parts.length < 2) return null
  return [parts[0], parts[1]]
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
    <div className="flex items-center gap-1.5" title={`${label}: ${pct}% of this repo's range`}>
      <span className="w-9 shrink-0 text-[10px] text-text-dim">{label}</span>
      <div className="h-1.5 w-16 shrink-0 overflow-hidden rounded-full bg-surface-2">
        <div
          className="h-full rounded-full bg-caution"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="metric w-8 shrink-0 text-right text-[11px] text-text-dim">
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

function BucketSummary({ functions }: { functions: FunctionMetric[] }) {
  const startHere = functions.filter((f) => f.bucket === 'start_here').length
  const dragons = functions.length - startHere
  return (
    <p className="mt-2 text-sm text-text-dim">
      <span className="text-safe">{startHere} Start Here</span>
      {' · '}
      <span className="text-danger">{dragons} Here Be Dragons</span>
    </p>
  )
}

export function RepoWorkspace() {
  const [repoInput, setRepoInput] = useState('')

  const analysis = useMutation({
    mutationFn: ([owner, name]: [string, string]) =>
      apiPostJson<RepoAnalysis>(`/repos/${owner}/${name}/analyze`),
  })

  const issues = useMutation({
    mutationFn: ([owner, name]: [string, string]) =>
      apiGet<RankedIssuesResponse>(`/repos/${owner}/${name}/issues`),
  })

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    const parsed = parseOwnerRepo(repoInput)
    if (!parsed) return
    analysis.mutate(parsed)
    issues.mutate(parsed)
  }

  return (
    <>
      <section className="mt-6 rounded-lg border border-border bg-surface-1 p-6">
        <h2 className="text-sm font-medium text-text-bright">
          Blast Radius Engine — analyze a repo
        </h2>
        <p className="mt-1 text-sm text-text-dim">
          Real tree-sitter parse + call graph + cyclomatic complexity + test
          proximity + git churn, computed live. No AI, no external API — just
          the repo you name.
        </p>

        <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
          <input
            type="text"
            value={repoInput}
            onChange={(e) => setRepoInput(e.target.value)}
            placeholder="owner/repo, e.g. pallets/itsdangerous"
            className="metric flex-1 rounded-md border border-border bg-surface-0 px-3 py-2 text-sm text-text-bright placeholder:text-text-dim"
          />
          <button
            type="submit"
            disabled={analysis.isPending}
            className="rounded-md bg-surface-2 px-4 py-2 text-sm font-medium text-text-bright hover:bg-border disabled:opacity-50"
          >
            {analysis.isPending ? 'Analyzing…' : 'Analyze'}
          </button>
        </form>

        {analysis.isPending && (
          <p className="mt-4 text-sm text-text-dim">
            Cloning, parsing every source file, walking git history, and
            building the call graph — first-time analysis of a repo can take
            a little while.
          </p>
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
            <p className="metric text-sm text-text-dim">
              {analysis.data.repo} @ {analysis.data.commit_sha.slice(0, 7)} —{' '}
              {analysis.data.file_count} files, {analysis.data.function_count}{' '}
              functions
            </p>
            <BucketSummary functions={analysis.data.functions} />
            <div className="mt-3 max-h-[32rem] overflow-y-auto rounded-md border border-border">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-surface-2 text-text-dim">
                  <tr>
                    <th className="px-3 py-2 font-medium">Function</th>
                    <th className="px-3 py-2 font-medium">File</th>
                    <th className="px-3 py-2 font-medium">Signals</th>
                    <th className="px-3 py-2 font-medium text-right">Test</th>
                    <th className="px-3 py-2 font-medium">Bucket</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.data.functions.map((fn) => (
                    <tr key={fn.id} className="border-t border-border align-top">
                      <td className="metric px-3 py-2 text-text-bright">
                        {fn.name}
                        {fn.name_is_ambiguous && (
                          <span className="ml-1 text-xs text-caution">
                            (ambiguous name)
                          </span>
                        )}
                      </td>
                      <td className="metric px-3 py-2 text-text-dim">
                        {fn.file}:{fn.start_line}
                      </td>
                      <td className="px-3 py-2">
                        <SignalBars fn={fn} />
                      </td>
                      <td className="metric px-3 py-2 text-right">
                        {fn.has_test_coverage ? (
                          <span className="text-safe">yes</span>
                        ) : (
                          <span className="text-text-dim">no</span>
                        )}
                      </td>
                      <td className="px-3 py-2">
                        <BucketBadge bucket={fn.bucket} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      {analysis.isSuccess && <ReadinessCard analysis={analysis.data} />}

      <section className="mt-6 rounded-lg border border-border bg-surface-1 p-6">
        <h2 className="text-sm font-medium text-text-bright">
          Recommended issues
        </h2>
        <p className="mt-1 text-sm text-text-dim">
          Local sentence embeddings rank open issues against your skill
          profile — overlapping terms shown are TF-IDF weighted, not a bare
          similarity float.
        </p>

        {issues.isPending && (
          <p className="mt-4 text-sm text-text-dim">Ranking open issues…</p>
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
            <ul className="mt-3 flex flex-col gap-3">
              {issues.data.issues.map((issue) => (
                <li
                  key={issue.number}
                  className="rounded-md border border-border p-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <a
                      href={issue.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm font-medium text-text-bright hover:underline"
                    >
                      #{issue.number} {issue.title}
                    </a>
                    <span className="metric shrink-0 text-xs text-text-dim">
                      similarity {issue.similarity.toFixed(3)}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-text-dim">{issue.explanation}</p>
                  {issue.overlapping_terms.length > 0 && (
                    <p className="mt-1 text-xs text-text-dim">
                      matched on:{' '}
                      <span className="metric text-text-bright">
                        {issue.overlapping_terms.join(', ')}
                      </span>
                    </p>
                  )}
                </li>
              ))}
            </ul>
            {issues.data.issues.length === 0 && (
              <p className="text-sm text-text-dim">
                This repo has no open issues right now — try another repo to
                see ranked recommendations.
              </p>
            )}
          </div>
        )}
      </section>
    </>
  )
}
