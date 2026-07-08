import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { ApiError, apiPostJson, type RepoAnalysis } from '../lib/api'

function parseOwnerRepo(input: string): [string, string] | null {
  let cleaned = input.trim()
  cleaned = cleaned.replace(/^https?:\/\//, '').replace(/^github\.com\//, '')
  cleaned = cleaned.replace(/\.git$/, '').replace(/\/+$/, '')
  const parts = cleaned.split('/').filter(Boolean)
  if (parts.length < 2) return null
  return [parts[0], parts[1]]
}

export function RepoAnalyzer() {
  const [repoInput, setRepoInput] = useState('')

  const mutation = useMutation({
    mutationFn: ([owner, name]: [string, string]) =>
      apiPostJson<RepoAnalysis>(`/repos/${owner}/${name}/analyze`),
  })

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    const parsed = parseOwnerRepo(repoInput)
    if (parsed) mutation.mutate(parsed)
  }

  return (
    <section className="mt-6 rounded-lg border border-border bg-surface-1 p-6">
      <h2 className="text-sm font-medium text-text-bright">
        Blast Radius Engine — analyze a repo
      </h2>
      <p className="mt-1 text-sm text-text-dim">
        Real tree-sitter parse + call graph + cyclomatic complexity, computed
        live. No AI, no external API — just the repo you name.
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
          disabled={mutation.isPending}
          className="rounded-md bg-surface-2 px-4 py-2 text-sm font-medium text-text-bright hover:bg-border disabled:opacity-50"
        >
          {mutation.isPending ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>

      {mutation.isPending && (
        <p className="mt-4 text-sm text-text-dim">
          Cloning, parsing every source file, and building the call graph —
          first-time analysis of a repo can take a little while.
        </p>
      )}

      {mutation.isError && (
        <p className="mt-4 text-sm text-danger">
          {mutation.error instanceof ApiError
            ? mutation.error.message
            : 'Analysis failed.'}
        </p>
      )}

      {mutation.isSuccess && (
        <div className="mt-4">
          <p className="metric text-sm text-text-dim">
            {mutation.data.repo} @ {mutation.data.commit_sha.slice(0, 7)} —{' '}
            {mutation.data.file_count} files, {mutation.data.function_count}{' '}
            functions
          </p>
          <div className="mt-3 max-h-96 overflow-y-auto rounded-md border border-border">
            <table className="w-full text-left text-sm">
              <thead className="sticky top-0 bg-surface-2 text-text-dim">
                <tr>
                  <th className="px-3 py-2 font-medium">Function</th>
                  <th className="px-3 py-2 font-medium">File</th>
                  <th className="px-3 py-2 font-medium text-right">Fan-in</th>
                  <th className="px-3 py-2 font-medium text-right">
                    Complexity
                  </th>
                </tr>
              </thead>
              <tbody>
                {mutation.data.functions.map((fn) => (
                  <tr key={fn.id} className="border-t border-border">
                    <td className="metric px-3 py-2 text-text-bright">
                      {fn.name}
                      {fn.name_is_ambiguous && (
                        <span className="ml-2 text-xs text-caution">
                          ambiguous name
                        </span>
                      )}
                    </td>
                    <td className="metric px-3 py-2 text-text-dim">
                      {fn.file}:{fn.start_line}
                    </td>
                    <td className="metric px-3 py-2 text-right">
                      {fn.fan_in}
                    </td>
                    <td className="metric px-3 py-2 text-right">
                      {fn.cyclomatic_complexity}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  )
}
