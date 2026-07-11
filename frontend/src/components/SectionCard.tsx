import type { ReactNode } from 'react'

type Accent = 'accent' | 'violet' | 'cyan' | 'none'

const ACCENT_CLASSES: Record<Accent, { badge: string; icon: string }> = {
  accent: { badge: 'bg-accent-bg', icon: 'text-accent-bright' },
  violet: { badge: 'bg-violet-bg', icon: 'text-violet' },
  cyan: { badge: 'bg-cyan-bg', icon: 'text-cyan' },
  none: { badge: 'bg-surface-2', icon: 'text-text-dim' },
}

export function SectionCard({
  icon,
  title,
  description,
  accent = 'accent',
  children,
}: {
  icon: ReactNode
  title: string
  description: string
  accent?: Accent
  children: ReactNode
}) {
  const classes = ACCENT_CLASSES[accent]
  return (
    <section className="mt-6 rounded-xl border border-border bg-surface-1 p-6 shadow-sm transition-colors hover:border-border-bright">
      <div className="flex items-start gap-3">
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${classes.badge} ${classes.icon}`}
        >
          {icon}
        </div>
        <div className="min-w-0">
          <h2 className="text-lg font-semibold text-text-bright">{title}</h2>
          <p className="mt-1 text-sm text-text-dim">{description}</p>
        </div>
      </div>
      <div className="mt-4">{children}</div>
    </section>
  )
}
