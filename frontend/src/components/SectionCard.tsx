import type { ReactNode } from 'react'

type Accent = 'accent' | 'violet' | 'cyan'

const ACCENT_CLASSES: Record<Accent, { badge: string; icon: string; topBorder: string }> = {
  accent: {
    badge: 'bg-accent-bg',
    icon: 'text-accent-bright',
    topBorder: 'from-accent/70',
  },
  violet: {
    badge: 'bg-violet-bg',
    icon: 'text-violet',
    topBorder: 'from-violet/70',
  },
  cyan: {
    badge: 'bg-cyan-bg',
    icon: 'text-cyan',
    topBorder: 'from-cyan/70',
  },
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
    <section className="relative mt-6 overflow-hidden rounded-xl border border-border bg-surface-1 p-6 shadow-lg shadow-black/20">
      <div
        className={`absolute inset-x-0 top-0 h-px bg-gradient-to-r ${classes.topBorder} to-transparent`}
      />
      <div className="flex items-start gap-3">
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${classes.badge} ${classes.icon}`}
        >
          {icon}
        </div>
        <div>
          <h2 className="text-sm font-medium text-text-bright">{title}</h2>
          <p className="mt-1 text-sm text-text-dim">{description}</p>
        </div>
      </div>
      <div className="mt-4">{children}</div>
    </section>
  )
}
