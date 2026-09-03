import { useState, useEffect } from 'react'

export function useToast() {
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    if (!toast) return

    const timer = window.setTimeout(() => setToast(null), 1800)
    return () => window.clearTimeout(timer)
  }, [toast])

  const showToast = (message: string) => {
    setToast(message)
  }

  return { toast, showToast }
}