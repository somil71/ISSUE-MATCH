import { Link } from 'react-router-dom'

const REPO_URL = 'https://github.com/somil71/ISSUE-MATCH'

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-8 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-3 text-sm text-text-dim">
          <span className="font-black tracking-tight text-accent-bright">
            IssueMatch AI
          </span>
          <span>
            No LLM calls, no external AI API — every number is computed live.
          </span>
        </div>
        <nav className="flex items-center gap-5 text-sm text-text-dim">
          <Link to="/how-it-works" className="transition-colors hover:text-text-bright">
            How it works
          </Link>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-text-bright"
          >
            Source
          </a>
        </nav>
      </div>
    </footer>
  )
}
