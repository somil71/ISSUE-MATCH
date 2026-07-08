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
