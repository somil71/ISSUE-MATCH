import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center py-16">
      <div className="w-full max-w-lg overflow-hidden rounded-xl border border-border bg-surface-1/70 p-8 text-center shadow-2xl shadow-black/30 backdrop-blur-md">
        <div className="mb-6 flex items-center justify-between border-b border-border pb-3">
          <div className="flex gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-danger" />
            <span className="h-2.5 w-2.5 rounded-full bg-border-bright" />
            <span className="h-2.5 w-2.5 rounded-full bg-border-bright" />
          </div>
          <span className="metric text-xs uppercase tracking-widest text-text-dim">
            sys.err.404
          </span>
        </div>

        <div className="metric text-8xl font-black leading-none text-danger">
          404
        </div>
        <h1 className="mt-4 text-lg font-semibold text-text-bright">
          Nothing resolves to this path.
        </h1>
        <p className="mt-2 text-sm text-text-dim">
          Same rule as everything else here — no page exists unless it's
          real. This one isn't.
        </p>

        <Link
          to="/"
          className="mt-6 inline-block rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-on-accent transition-colors hover:bg-accent-bright"
        >
          Back to the workspace
        </Link>

        <div className="mt-6 flex items-center justify-center gap-2 text-xs text-text-dim">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-danger opacity-75 motion-reduce:animate-none" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-danger" />
          </span>
          Route not found.
        </div>
      </div>
    </div>
  )
}
