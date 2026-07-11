import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from 'react'

type ToastTone = 'default' | 'success' | 'error'
interface ToastEntry {
  id: number
  message: string
  tone: ToastTone
}

const ToastContext = createContext<{
  push: (message: string, tone?: ToastTone) => void
} | null>(null)

const TONE_CLASSES: Record<ToastTone, string> = {
  default: 'border-border bg-surface-1 text-text-bright',
  success: 'border-safe/30 bg-safe-bg text-safe',
  error: 'border-danger/30 bg-danger-bg text-danger',
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastEntry[]>([])

  const push = useCallback((message: string, tone: ToastTone = 'default') => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { id, message, tone }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 2600)
  }, [])

  return (
    <ToastContext.Provider value={{ push }}>
      {children}
      <div className="pointer-events-none fixed inset-x-0 bottom-5 z-50 flex flex-col items-center gap-2 px-4">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`pointer-events-auto rounded-lg border px-4 py-2.5 text-sm shadow-lg backdrop-blur motion-safe:animate-[toast-in_0.18s_ease-out] ${TONE_CLASSES[t.tone]}`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
