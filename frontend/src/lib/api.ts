const API_BASE = '/api'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
  })
  if (!res.ok) {
    throw new ApiError(`GET ${path} failed with ${res.status}`, res.status)
  }
  return res.json() as Promise<T>
}

export interface HealthStatus {
  status: 'ok' | 'degraded'
  services: {
    database: 'ok' | 'error'
    cache: 'ok' | 'error'
  }
}

export interface CurrentUser {
  id: number
  username: string
  avatar_url: string
  skills: string[]
  experience_level: string | null
}

export async function apiPost(path: string): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) {
    throw new ApiError(`POST ${path} failed with ${res.status}`, res.status)
  }
}

export async function apiPostJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new ApiError(
      body?.detail || `POST ${path} failed with ${res.status}`,
      res.status,
    )
  }
  return res.json() as Promise<T>
}

export async function apiPatchJson<T>(path: string, payload: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'PATCH',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new ApiError(
      body?.detail || `PATCH ${path} failed with ${res.status}`,
      res.status,
    )
  }
  return res.json() as Promise<T>
}

export type BlastRadiusBucket = 'start_here' | 'here_be_dragons'

export interface FunctionMetric {
  id: string
  name: string
  file: string
  start_line: number
  end_line: number
  fan_in: number
  transitive_fan_in: number
  name_is_ambiguous: boolean
  cyclomatic_complexity: number
  has_test_coverage: boolean
  churn_intensity: number
  normalized_fan_in: number
  normalized_complexity: number
  normalized_churn: number
  blast_radius_score: number
  bucket: BlastRadiusBucket
  summary: string
}

export interface SkillGap {
  required: string[]
  have: string[]
  gap: string[]
}

export interface RepoAnalysis {
  repo: string
  commit_sha: string
  default_branch: string
  file_count: number
  function_count: number
  functions: FunctionMetric[]
  skill_gap: SkillGap
  avg_blast_radius_score: number
  readiness_score: number
}

export interface IssueLabel {
  name: string
  color: string
}

export interface CodeReference {
  name: string | null
  file: string
  bucket: BlastRadiusBucket | null
  summary: string | null
}

export interface RankedIssue {
  number: number
  title: string
  url: string
  labels: IssueLabel[]
  similarity: number
  overlapping_terms: string[]
  explanation: string
  beginner_friendly_label: boolean
  code_references: CodeReference[]
  draft_comment: string
}

export interface LabelDisagreement {
  number: number
  title: string
  url: string
  risky_reference: CodeReference
}

export interface LabelAccuracy {
  github_labeled_count: number
  verified_count: number
  disagreement_count: number
  disagreements: LabelDisagreement[]
}

export interface RankedIssuesResponse {
  repo: string
  user_skills: string[]
  inferred_skills: string[]
  analyzed: boolean
  issues: RankedIssue[]
  label_accuracy: LabelAccuracy
}

export interface NetworkTrustSummary {
  total_calls: number
  hosts: { host: string; count: number }[]
  since: string | null
}

export interface BlastMapNode {
  id: string
  name: string
  file: string
  start_line: number
  bucket: BlastRadiusBucket
  score: number
  hops: number
}

export interface BlastMapEdge {
  source: string
  target: string
}

export interface BlastMapResponse {
  function_id: string
  max_hops: number
  total_transitive_dependents: number
  nodes: BlastMapNode[]
  edges: BlastMapEdge[]
}
