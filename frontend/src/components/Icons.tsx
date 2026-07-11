type IconProps = { className?: string }

export function ShieldIcon({ className = 'h-4 w-4' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M12 3 4.5 5.6v5.2c0 4.8 3.2 8.9 7.5 10.2 4.3-1.3 7.5-5.4 7.5-10.2V5.6L12 3Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="m8.7 12.2 2.3 2.3 4.3-4.7"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function TargetIcon({ className = 'h-4 w-4' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6" opacity="0.4" />
      <circle cx="12" cy="12" r="5.5" stroke="currentColor" strokeWidth="1.6" opacity="0.75" />
      <circle cx="12" cy="12" r="2" fill="currentColor" />
    </svg>
  )
}

export function TagIcon({ className = 'h-4 w-4' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M11.2 3.2 3.2 11.2a1.5 1.5 0 0 0 0 2.12l7.46 7.46a1.5 1.5 0 0 0 2.12 0l8-8a1.5 1.5 0 0 0 .44-1.06V4.7a1.5 1.5 0 0 0-1.5-1.5h-7.05c-.4 0-.78.16-1.06.44Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <circle cx="16" cy="8" r="1.4" fill="currentColor" />
    </svg>
  )
}

export function SparklesIcon({ className = 'h-4 w-4' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M11 3.5 12.4 8l4.6 1.4L12.4 10.8 11 15.3 9.6 10.8 5 9.4l4.6-1.4L11 3.5Z"
        fill="currentColor"
      />
      <path
        d="M18 13.5l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8.8-2.2Z"
        fill="currentColor"
        opacity="0.7"
      />
    </svg>
  )
}

export function GaugeIcon({ className = 'h-4 w-4' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M4 15a8 8 0 1 1 16 0"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <path d="M12 15 16 9.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="12" cy="15" r="1.4" fill="currentColor" />
    </svg>
  )
}

export function RouteIcon({ className = 'h-4 w-4' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M5 8.2C5 13 8 15 12 15.8M13.6 17C16 16 18 13 19 11.2"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <circle cx="5" cy="6" r="2.2" fill="currentColor" />
      <circle cx="12" cy="18" r="2.2" fill="currentColor" opacity="0.85" />
      <circle cx="19" cy="9" r="2.2" fill="currentColor" opacity="0.6" />
    </svg>
  )
}

export function TerminalIcon({ className = 'h-4 w-4' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <rect x="3" y="4.5" width="18" height="15" rx="2" stroke="currentColor" strokeWidth="1.6" />
      <path d="m7 9.5 3 2.7-3 2.7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M13 14.9h4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}

export function LandmarkIcon({ className = 'h-4 w-4' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M12 3v18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M12 4.5 19 7.5 12 10.5Z" fill="currentColor" opacity="0.8" />
      <path d="M7 21h10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}
