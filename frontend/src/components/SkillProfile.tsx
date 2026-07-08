import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiPatchJson, type CurrentUser } from '../lib/api'

const EXPERIENCE_LEVELS = ['beginner', 'intermediate', 'advanced'] as const

export function SkillProfile({ user }: { user: CurrentUser }) {
  const queryClient = useQueryClient()
  const [skillsInput, setSkillsInput] = useState(user.skills.join(', '))
  const [experienceLevel, setExperienceLevel] = useState(
    user.experience_level ?? '',
  )

  const mutation = useMutation({
    mutationFn: (payload: { skills: string[]; experience_level: string | null }) =>
      apiPatchJson<CurrentUser>('/users/me', payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(['session'], updated)
    },
  })

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    const skills = skillsInput
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    mutation.mutate({
      skills,
      experience_level: experienceLevel || null,
    })
  }

  return (
    <section className="mt-6 rounded-lg border border-border bg-surface-1 p-6">
      <h2 className="text-sm font-medium text-text-bright">Your skill profile</h2>
      <p className="mt-1 text-sm text-text-dim">
        Used for issue matching (Feature 2) — compared against issue text via
        local sentence embeddings, no external API.
      </p>

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3">
        <label className="text-sm text-text-dim">
          Skills (comma-separated)
          <input
            type="text"
            value={skillsInput}
            onChange={(e) => setSkillsInput(e.target.value)}
            placeholder="Python, FastAPI, React"
            className="metric mt-1 w-full rounded-md border border-border bg-surface-0 px-3 py-2 text-sm text-text-bright placeholder:text-text-dim"
          />
        </label>

        <label className="text-sm text-text-dim">
          Experience level
          <select
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
            className="mt-1 w-full rounded-md border border-border bg-surface-0 px-3 py-2 text-sm text-text-bright"
          >
            <option value="">Unspecified</option>
            {EXPERIENCE_LEVELS.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>
        </label>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="self-start rounded-md bg-surface-2 px-4 py-2 text-sm font-medium text-text-bright hover:bg-border disabled:opacity-50"
        >
          {mutation.isPending ? 'Saving…' : 'Save profile'}
        </button>

        {mutation.isSuccess && (
          <span className="text-sm text-safe">Saved.</span>
        )}
      </form>
    </section>
  )
}
