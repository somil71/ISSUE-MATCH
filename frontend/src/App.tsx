import { Link, Route, Routes, useLocation } from 'react-router-dom'
import { AuthPanel } from './components/AuthPanel'
import { Footer } from './components/Footer'
import { SystemStatus } from './components/SystemStatus'
import { TrustPanel } from './components/TrustPanel'
import { HomePage } from './pages/HomePage'
import { HowItWorksPage } from './pages/HowItWorksPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { SettingsPage } from './pages/SettingsPage'
import { useSession } from './lib/session'

function NavLink({ to, children }: { to: string; children: string }) {
  const { pathname } = useLocation()
  const active = pathname === to
  return (
    <Link
      to={to}
      className={`text-sm transition-colors ${
        active
          ? 'font-medium text-text-bright'
          : 'text-text-dim hover:text-text-bright'
      }`}
    >
      {children}
    </Link>
  )
}

function App() {
  const { data: user } = useSession()

  return (
    <div className="flex min-h-svh flex-col">
      <header className="sticky top-0 z-10 border-b border-border bg-surface-0/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-8 px-6 py-4">
          <Link to="/" className="text-base font-bold tracking-tight text-text-bright">
            IssueMatch<span className="text-accent-bright">AI</span>
          </Link>

          {user && (
            <nav className="hidden items-center gap-6 md:flex">
              <NavLink to="/">Dashboard</NavLink>
              <NavLink to="/how-it-works">How it works</NavLink>
              <NavLink to="/settings">Settings</NavLink>
            </nav>
          )}

          <div className="ml-auto flex items-center gap-1">
            <TrustPanel />
            <SystemStatus />
            <div className="mx-2 h-5 w-px bg-border" />
            <AuthPanel />
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
        <Routes>
          <Route path="/" element={<HomePage user={user} />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>

      <Footer />
    </div>
  )
}

export default App
