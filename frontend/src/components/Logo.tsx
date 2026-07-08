export function Logo({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5" opacity="0.35" />
      <circle cx="12" cy="12" r="5.5" stroke="currentColor" strokeWidth="1.5" opacity="0.7" />
      <circle cx="12" cy="12" r="2" fill="currentColor" />
    </svg>
  )
}
