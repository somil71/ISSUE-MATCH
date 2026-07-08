const API_BASE = '/api'

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message)
    this.name = 'ApiError'
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

export interface FunctionMetric {
  id: string
  name: string
  file: string
  start_line: number
  end_line: number
  fan_in: number
  name_is_ambiguous: boolean
  cyclomatic_complexity: number
}

export interface RepoAnalysis {
  repo: string
  commit_sha: string
  default_branch: string
  file_count: number
  function_count: number
  functions: FunctionMetric[]
}
