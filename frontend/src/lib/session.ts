import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError, apiGet, apiPost, type CurrentUser } from './api'

export function useSession() {
  const queryClient = useQueryClient()

  const query = useQuery<CurrentUser | null>({
    queryKey: ['session'],
    queryFn: async () => {
      try {
        return await apiGet<CurrentUser>('/auth/me')
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null
        throw err
      }
    },
  })

  const logout = async () => {
    await apiPost('/auth/logout')
    queryClient.setQueryData(['session'], null)
  }

  return { ...query, logout }
}

export function loginWithGitHub() {
  window.location.href = '/api/auth/login'
}
