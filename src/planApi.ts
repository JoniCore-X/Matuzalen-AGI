import { supabase } from './supabaseClient'

export type GeneratedPlan = {
  goal_title: string
  summary: string
  assumptions: string[]
  missing_info: string[]
  warnings: string[]
  stages: Array<{
    title: string
    description: string | null
    position: number
    tasks: Array<{
      title: string
      description: string | null
      priority: 'high' | 'medium' | 'low'
      estimated_minutes: number
      depends_on: string[]
    }>
  }>
}

const apiBaseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export async function generatePlanWithAi(goal: string): Promise<GeneratedPlan> {
  const { data: sessionData } = await supabase.auth.getSession()
  const accessToken = sessionData.session?.access_token

  if (!accessToken) {
    throw new Error('Inicia sesion para generar un plan')
  }

  const response = await fetch(`${apiBaseUrl}/plans/generate`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ goal }),
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? 'No se pudo generar el plan')
  }

  const body = (await response.json()) as { plan: GeneratedPlan }
  return body.plan
}
