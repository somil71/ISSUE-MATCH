import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiPatchJson, type CurrentUser } from '../lib/api'
import { useToast } from '../lib/toast'
import { TagIcon } from './Icons'
import { SectionCard } from './SectionCard'

const EXPERIENCE_LEVELS = ['beginner', 'intermediate', 'advanced'] as const

export function SkillProfile({ user }: { user: CurrentUser }) {
  const queryClient = useQueryClient()
  const toast = useToast()
  const [skills, setSkills] = useState<string[]>(user.skills)
  const [draft, setDraft] = useState('')
  const [experienceLevel, setExperienceLevel] = useState(
    user.experience_level ?? '',
  )

  const mutation = useMutation({
    mutationFn: (payload: { skills: string[]; experience_level: string | null }) =>
      apiPatchJson<CurrentUser>('/users/me', payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(['session'], updated)
      toast.push('Profile saved.', 'success')
    },
    onError: () => {
      toast.push('Could not save your profile — try again.', 'error')
    },
  })

  const addSkill = () => {
    const trimmed = draft.trim()
    if (trimmed && !skills.some((s) => s.toLowerCase() === trimmed.toLowerCase())) {
      setSkills([...skills, trimmed])
    }
    setDraft('')
  }

  const removeSkill = (skill: string) => {
    setSkills(skills.filter((s) => s !== skill))
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      addSkill()
    } else if (event.key === 'Backspace' && draft === '' && skills.length > 0) {
      setSkills(skills.slice(0, -1))
    }
  }

  const handleSave = () => {
    mutation.mutate({ skills, experience_level: experienceLevel || null })
  }

  return (
    <SectionCard
      icon={<TagIcon />}
      title="Your skill profile"
      description="Compared against issue text via local sentence embeddings — no external API."
      accent="accent"
    >
      <div
        className="flex flex-wrap items-center gap-2 rounded-lg border border-border bg-surface-0 p-2 focus-within:border-accent"
        onClick={(e) => {
          if (e.currentTarget === e.target) {
            e.currentTarget.querySelector('input')?.focus()
          }
        }}
      >
        {skills.map((skill) => (
          <span
            key={skill}
            className="metric flex items-center gap-1.5 rounded-full bg-accent-bg px-2.5 py-1 text-xs text-accent-bright"
          >
            {skill}
            <button
              type="button"
              onClick={() => removeSkill(skill)}
              aria-label={`Remove ${skill}`}
              className="text-accent-bright/60 hover:text-accent-bright"
            >
              ×
            </button>
          </span>
        ))}
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            skills.length === 0 ? 'Type a skill and press Enter…' : 'Add another…'
          }
          className="metric min-w-[12ch] flex-1 bg-transparent px-1 py-1 text-sm text-text-bright placeholder:text-text-dim focus:outline-none"
        />
      </div>

      <div className="mt-4">
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
          type="button"
          onClick={handleSave}
          disabled={mutation.isPending}
          className="mt-3 w-full rounded-md bg-accent px-4 py-2 text-sm font-medium text-on-accent transition-colors hover:bg-accent-bright disabled:opacity-50"
        >
          {mutation.isPending ? 'Saving…' : 'Save profile'}
        </button>
      </div>
    </SectionCard>
  )
}
