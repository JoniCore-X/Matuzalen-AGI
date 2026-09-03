import type { Session } from '@supabase/supabase-js'
import { useEffect, useMemo, useState } from 'react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import type { DropResult } from '@hello-pangea/dnd'
import './App.css'
import { generatePlanWithAi } from './planApi'
import { supabase } from './supabaseClient'
import { useLocalStorage } from './hooks/useLocalStorage'
import { useToast } from './hooks/useToast'

type Priority = 'Alta' | 'Media' | 'Baja'
type TaskFilter = 'all' | 'pending' | 'done'
type PriorityFilter = 'all' | 'Alta' | 'Media' | 'Baja'
type DateFilter = 'all' | 'today' | 'week' | 'month'
type ReminderMode = 'Diario' | 'Semanal' | 'Personalizado'

type Task = {
  id: string
  title: string
  duration: string
  priority: Priority
  date: string
  done: boolean
  tags: string[]
}

type Phase = {
  id: string
  name: string
  duration: string
  description: string
  tasks: Task[]
}

type Plan = {
  goal: string
  totalDuration: string
  nextReminder: string
  progress: number
  phases: Phase[]
}

type HistoryEntry = {
  id: string
  goal: string
  createdAt: string
  totalDuration: string
  progress: number
}

type Statistics = {
  totalPlans: number
  totalTasks: number
  completedTasks: number
  averageProgress: number
  highPriorityTasks: number
  tasksThisWeek: number
  completionRate: number
}

type TaskFormState = {
  title: string
  duration: string
  priority: Priority
}

const STORAGE_KEY = 'planbot-mvp-v1'
const HISTORY_KEY = 'planbot-history-v1'
const DEFAULT_GOAL = 'Quiero lanzar mi curso en 30 días'
let idSequence = 0

function createId(prefix: string) {
  idSequence += 1
  return `${prefix}-${Date.now()}-${idSequence}`
}

function formatDate(offsetDays: number) {
  const date = new Date()
  date.setDate(date.getDate() + offsetDays)

  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: 'short',
  })
}

function makeTask(title: string, duration: string, priority: Priority, offsetDays: number, done = false, tags: string[] = []): Task {
  return {
    id: createId('task'),
    title,
    duration,
    priority,
    date: formatDate(offsetDays),
    done,
    tags,
  }
}

function mapPriority(priority: 'high' | 'medium' | 'low'): Priority {
  const priorities: Record<'high' | 'medium' | 'low', Priority> = {
    high: 'Alta',
    medium: 'Media',
    low: 'Baja',
  }
  return priorities[priority]
}

function formatDuration(minutes: number) {
  if (minutes < 60) return `${minutes} min`
  if (minutes % 60 === 0) return `${minutes / 60} h`
  return `${Math.floor(minutes / 60)} h ${minutes % 60} min`
}

function getProgress(plan: Plan) {
  const taskCount = plan.phases.reduce((sum, phase) => sum + phase.tasks.length, 0)
  if (taskCount === 0) return 0

  const doneCount = plan.phases.reduce(
    (sum, phase) => sum + phase.tasks.filter((task) => task.done).length,
    0,
  )

  return Math.round((doneCount / taskCount) * 100)
}

function getReminderText(mode: ReminderMode, goal: string) {
  const base = goal.length > 30 ? goal.slice(0, 30) + '…' : goal

  switch (mode) {
    case 'Diario':
      return `Revisa hoy tu avance para ${base}`
    case 'Semanal':
      return `Haz una revisión semanal de ${base}`
    default:
      return `Entrena una sesión personalizada para ${base}`
  }
}

function calculateStatistics(plan: Plan, history: HistoryEntry[]): Statistics {
  const totalTasks = plan.phases.reduce((sum, phase) => sum + phase.tasks.length, 0)
  const completedTasks = plan.phases.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0)
  const highPriorityTasks = plan.phases.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.priority === 'Alta').length, 0)
  
  const currentProgress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
  const totalPlans = history.length + 1
  const averageProgress = history.length > 0 
    ? Math.round((history.reduce((sum, entry) => sum + entry.progress, 0) + currentProgress) / totalPlans)
    : currentProgress
  
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  const tasksThisWeek = plan.phases.reduce((sum, phase) => 
    sum + phase.tasks.filter((task) => {
      const taskDate = new Date(task.date)
      return taskDate >= oneWeekAgo && task.done
    }).length, 0
  )
  
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  return {
    totalPlans,
    totalTasks,
    completedTasks,
    averageProgress,
    highPriorityTasks,
    tasksThisWeek,
    completionRate
  }
}

function generatePlan(input: string): Plan {
  const text = input.trim() || DEFAULT_GOAL
  const lower = text.toLowerCase()

  if (lower.includes('curso')) {
    return {
      goal: text,
      totalDuration: '30 días',
      nextReminder: getReminderText('Semanal', text),
      progress: 0,
      phases: [
        {
          id: createId('phase'),
          name: 'Diseño del curso',
          duration: '5 días',
          description: 'Definir público, estructura y mapa del curso.',
          tasks: [
            makeTask('Definir público objetivo', '1 día', 'Alta', 1, false, ['investigación', 'estrategia']),
            makeTask('Mapear módulos y objetivos', '2 días', 'Alta', 3, false, ['planificación']),
            makeTask('Crear outline del curso', '2 días', 'Media', 5, false, ['contenido']),
          ],
        },
        {
          id: createId('phase'),
          name: 'Producción de contenido',
          duration: '10 días',
          description: 'Preparar videos, materiales y recursos del curso.',
          tasks: [
            makeTask('Escribir guiones', '3 días', 'Alta', 7, false, ['contenido', 'escritura']),
            makeTask('Grabar lecciones', '5 días', 'Alta', 10, false, ['video', 'producción']),
            makeTask('Preparar recursos descargables', '2 días', 'Media', 13, false, ['materiales']),
          ],
        },
        {
          id: createId('phase'),
          name: 'Lanzamiento',
          duration: '8 días',
          description: 'Armar la oferta, vender y preparar la publicación.',
          tasks: [
            makeTask('Diseñar landing page', '3 días', 'Alta', 15, false, ['diseño', 'marketing']),
            makeTask('Configurar checkout y pagos', '2 días', 'Alta', 18, false, ['técnico', 'ventas']),
            makeTask('Preparar campaña de email', '3 días', 'Media', 21, false, ['marketing', 'ventas']),
          ],
        },
      ],
    }
  }

  if (lower.includes('aprender') || lower.includes('estudi')) {
    return {
      goal: text,
      totalDuration: '6 semanas',
      nextReminder: getReminderText('Diario', text),
      progress: 0,
      phases: [
        {
          id: createId('phase'),
          name: 'Fundamentos',
          duration: '2 semanas',
          description: 'Aprender conceptos base y crear la base del proyecto.',
          tasks: [
            makeTask('Mapear temas clave', '1 semana', 'Alta', 2, false, ['planificación']),
            makeTask('Repasar conceptos básicos', '1 semana', 'Alta', 5, false, ['estudio']),
            makeTask('Hacer ejercicios simples', '3 días', 'Media', 8, false, ['práctica']),
          ],
        },
        {
          id: createId('phase'),
          name: 'Práctica',
          duration: '2 semanas',
          description: 'Aplicar los conocimientos con tareas reales.',
          tasks: [
            makeTask('Construir mini proyecto', '1 semana', 'Alta', 12, false, ['práctica', 'proyecto']),
            makeTask('Resolver ejercicios', '4 días', 'Alta', 15, false, ['práctica']),
            makeTask('Anotar dudas y bloqueos', '2 días', 'Media', 18, false, ['estudio']),
          ],
        },
      ],
    }
  }

  return {
    goal: text,
    totalDuration: '21 días',
    nextReminder: getReminderText('Personalizado', text),
    progress: 0,
    phases: [
      {
        id: createId('phase'),
        name: 'Enfoque',
        duration: '5 días',
        description: 'Definir dirección, objetivo y alcance del proyecto.',
        tasks: [
          makeTask('Definir el objetivo principal', '1 día', 'Alta', 1, false, ['planificación']),
          makeTask('Delimitar alcance', '2 días', 'Alta', 3, false, ['planificación']),
          makeTask('Alinear recursos necesarios', '2 días', 'Media', 5, false, ['recursos']),
        ],
      },
      {
        id: createId('phase'),
        name: 'Construcción',
        duration: '8 días',
        description: 'Ejecutar las tareas principales que generan valor.',
        tasks: [
          makeTask('Crear la primera versión', '3 días', 'Alta', 8, false, ['desarrollo']),
          makeTask('Revisar entregables', '2 días', 'Alta', 11, false, ['revisión']),
          makeTask('Aplicar ajustes', '3 días', 'Media', 14, false, ['mejora']),
        ],
      },
    ],
  }
}

function App() {
  const [goal, setGoal] = useState(DEFAULT_GOAL)
  const [plan, setPlan] = useState<Plan>(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return generatePlan(DEFAULT_GOAL)

    try {
      const parsed = JSON.parse(saved) as Plan
      return parsed.goal ? parsed : generatePlan(DEFAULT_GOAL)
    } catch {
      return generatePlan(DEFAULT_GOAL)
    }
  })
  const [approved, setApproved] = useState(false)
  const [taskFilter, setTaskFilter] = useState<TaskFilter>('all')
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>('all')
  const [dateFilter, setDateFilter] = useState<DateFilter>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [reminderMode, setReminderMode] = useState<ReminderMode>('Semanal')
  const [history, setHistory] = useLocalStorage<HistoryEntry[]>(HISTORY_KEY, [])
  const [taskForms, setTaskForms] = useState<Record<string, TaskFormState>>({})
  const { toast, showToast } = useToast()
  const [isGenerating, setIsGenerating] = useState(false)
  const [session, setSession] = useState<Session | null>(null)
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authMode, setAuthMode] = useState<'login' | 'register' | 'forgot'>('login')
  const [view, setView] = useState<'landing' | 'auth'>('landing')
  const [authMessage, setAuthMessage] = useState<string | null>(null)
  const [isAuthenticating, setIsAuthenticating] = useState(false)
  const [isPasswordVisible, setIsPasswordVisible] = useState(false)
  const [isSessionLoading, setIsSessionLoading] = useState(true)
  const [isLightTheme, setIsLightTheme] = useState(false)
  const [showStatistics, setShowStatistics] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [tagInput, setTagInput] = useState<Record<string, string>>({})
  const [availableTags, setAvailableTags] = useState<string[]>(() => {
    const allTags = new Set<string>()
    plan.phases.forEach(phase => {
      phase.tasks.forEach(task => {
        task.tags.forEach(tag => allTags.add(tag))
      })
    })
    return Array.from(allTags)
  })

  useEffect(() => {
    void supabase.auth.getSession().then(({ data }) => {
      setSession(data.session)
      setIsSessionLoading(false)
    })
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
    })

    return () => listener.subscription.unsubscribe()
  }, [])

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(plan))
  }, [plan])

  const totalTasks = useMemo(
    () => plan.phases.reduce((sum, phase) => sum + phase.tasks.length, 0),
    [plan],
  )

  const completedTasks = useMemo(
    () => plan.phases.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.done).length, 0),
    [plan],
  )

  const progress = useMemo(() => {
    if (totalTasks === 0) return 0
    return Math.round((completedTasks / totalTasks) * 100)
  }, [completedTasks, totalTasks])

  const visiblePhases = useMemo(
    () =>
      plan.phases.map((phase) => ({
        ...phase,
        tasks: phase.tasks.filter((task) => {
          // Filter by completion status
          if (taskFilter === 'pending' && task.done) return false
          if (taskFilter === 'done' && !task.done) return false

          // Filter by priority
          if (priorityFilter !== 'all' && task.priority !== priorityFilter) return false

          // Filter by search query
          if (searchQuery && !task.title.toLowerCase().includes(searchQuery.toLowerCase())) return false

          // Filter by date
          if (dateFilter !== 'all') {
            const taskDate = new Date(task.date)
            const today = new Date()
            today.setHours(0, 0, 0, 0)
            
            const weekFromNow = new Date(today)
            weekFromNow.setDate(weekFromNow.getDate() + 7)
            
            const monthFromNow = new Date(today)
            monthFromNow.setMonth(monthFromNow.getMonth() + 1)

            if (dateFilter === 'today' && taskDate.toDateString() !== today.toDateString()) return false
            if (dateFilter === 'week' && (taskDate < today || taskDate > weekFromNow)) return false
            if (dateFilter === 'month' && (taskDate < today || taskDate > monthFromNow)) return false
          }

          return true
        }),
      })),
    [plan, taskFilter, priorityFilter, dateFilter, searchQuery],
  )

  const statistics = useMemo(() => calculateStatistics(plan, history), [plan, history])

  const pushHistory = (nextPlan: Plan) => {
    const snapshot: HistoryEntry = {
      id: createId('history'),
      goal: nextPlan.goal,
      createdAt: new Date().toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
      }),
      totalDuration: nextPlan.totalDuration,
      progress: getProgress(nextPlan),
    }

    setHistory((current) => [snapshot, ...current].slice(0, 5))
  }

  const handleGenerate = async () => {
    if (!goal.trim()) {
      return
    }

    setIsGenerating(true)

    try {
      const generated = await generatePlanWithAi(goal.trim())
      const nextPlan: Plan = {
        goal: generated.goal_title,
        totalDuration: `${generated.stages.length} etapas`,
        nextReminder: getReminderText(reminderMode, generated.goal_title),
        progress: 0,
        phases: generated.stages.map((stage) => ({
          id: createId('phase'),
          name: stage.title,
          duration: `${stage.tasks.length} tareas`,
          description: stage.description ?? '',
          tasks: stage.tasks.map((task, index) =>
            makeTask(
              task.title,
              formatDuration(task.estimated_minutes),
              mapPriority(task.priority),
              index + 1,
              false,
              [], // AI-generated tasks start without tags
            ),
          ),
        })),
      }

      setGoal(generated.goal_title)
      setPlan(nextPlan)
      setApproved(false)
      pushHistory(nextPlan)
      showToast('Plan generado con IA')
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'No se pudo generar el plan')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleAuthentication = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setAuthMessage(null)
    setIsAuthenticating(true)

    if (authMode === 'register' && authPassword.length < 8) {
      setAuthMessage('Usa una contrasena de al menos 8 caracteres.')
      setIsAuthenticating(false)
      return
    }

    if (authMode === 'forgot') {
      const { error } = await supabase.auth.resetPasswordForEmail(authEmail.trim(), {
        redirectTo: window.location.origin,
      })
      setIsAuthenticating(false)
      setAuthMessage(error ? error.message : 'Te enviamos un enlace para restablecer tu contrasena.')
      return
    }

    const credentials = { email: authEmail.trim(), password: authPassword }
    try {
      const result = authMode === 'login'
        ? await supabase.auth.signInWithPassword(credentials)
        : await supabase.auth.signUp({
            ...credentials,
            options: { emailRedirectTo: window.location.origin },
          })

      if (result.error) {
        setAuthMessage(result.error.message)
        return
      }
      if (!result.data.session) {
        setAuthMessage('Revisa tu correo para confirmar tu cuenta.')
      }
    } finally {
      setIsAuthenticating(false)
    }
  }

  const handleMagicLink = async () => {
    if (!authEmail.trim()) {
      setAuthMessage('Escribe tu correo para recibir un enlace de acceso.')
      return
    }
    setIsAuthenticating(true)
    try {
      const { error } = await supabase.auth.signInWithOtp({
        email: authEmail.trim(),
        options: { emailRedirectTo: window.location.origin },
      })
      setAuthMessage(error ? error.message : 'Revisa tu correo para abrir tu enlace de acceso.')
    } finally {
      setIsAuthenticating(false)
    }
  }

  const handleGoogleSignIn = async () => {
    setAuthMessage(null)
    setIsAuthenticating(true)
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: window.location.origin },
      })
      if (error) setAuthMessage(error.message)
    } finally {
      setIsAuthenticating(false)
    }
  }

  const handleTaskToggle = (taskId: string) => {
    const updated = {
      ...plan,
      phases: plan.phases.map((phase) => ({
        ...phase,
        tasks: phase.tasks.map((task) =>
          task.id === taskId ? { ...task, done: !task.done } : task,
        ),
      })),
    }

    updated.progress = getProgress(updated)
    setPlan(updated)
  }

  const handleDeleteTask = (phaseId: string, taskId: string) => {
    const updated = {
      ...plan,
      phases: plan.phases.map((phase) =>
        phase.id === phaseId
          ? { ...phase, tasks: phase.tasks.filter((task) => task.id !== taskId) }
          : phase,
      ),
    }

    updated.progress = getProgress(updated)
    setPlan(updated)
  }

  const handleAddTask = (phaseId: string) => {
    const formState = taskForms[phaseId] ?? {
      title: '',
      duration: '1 día',
      priority: 'Media' as Priority,
    }

    if (!formState.title.trim()) {
      showToast('Escribe el nombre de la tarea')
      return
    }

    const tagsInput = tagInput[phaseId] || ''
    const newTags = tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0)
    
    // Update available tags
    setAvailableTags(prev => {
      const newSet = new Set([...prev, ...newTags])
      return Array.from(newSet)
    })

    const newTask = makeTask(
      formState.title.trim(),
      formState.duration,
      formState.priority,
      1,
      false,
      newTags
    )

    const updated = {
      ...plan,
      phases: plan.phases.map((phase) =>
        phase.id === phaseId ? { ...phase, tasks: [...phase.tasks, newTask] } : phase,
      ),
    }

    updated.progress = getProgress(updated)
    setPlan(updated)
    setTaskForms((current) => ({
      ...current,
      [phaseId]: { title: '', duration: '1 día', priority: 'Media' },
    }))
    setTagInput((current) => ({
      ...current,
      [phaseId]: '',
    }))
    showToast('Tarea añadida')
  }

  const handleRemoveTag = (phaseId: string, taskId: string, tag: string) => {
    const updated = {
      ...plan,
      phases: plan.phases.map((phase) =>
        phase.id === phaseId
          ? {
              ...phase,
              tasks: phase.tasks.map((task) =>
                task.id === taskId
                  ? { ...task, tags: task.tags.filter((t) => t !== tag) }
                  : task,
              ),
            }
          : phase,
      ),
    }

    setPlan(updated)
    showToast('Etiqueta eliminada')
  }

  const handleApprove = () => {
    setApproved(true)
    pushHistory(plan)
    showToast('Plan confirmado')
  }

  const handleReset = () => {
    const initial = generatePlan(DEFAULT_GOAL)
    setGoal(DEFAULT_GOAL)
    setPlan({ ...initial, nextReminder: getReminderText('Semanal', DEFAULT_GOAL) })
    setApproved(false)
    setTaskFilter('all')
    setReminderMode('Semanal')
  }

  const handleHistorySelect = (entry: HistoryEntry) => {
    const nextPlan = {
      ...generatePlan(entry.goal),
      nextReminder: getReminderText(reminderMode, entry.goal),
    }

    setGoal(entry.goal)
    setPlan(nextPlan)
    setApproved(false)
    showToast('Plan cargado del historial')
  }

  const handleDragEnd = (result: DropResult) => {
    const { source, destination, type } = result

    if (!destination) return

    if (type === 'PHASE') {
      // Reorder phases
      const newPhases = Array.from(plan.phases)
      const [removed] = newPhases.splice(source.index, 1)
      newPhases.splice(destination.index, 0, removed)

      setPlan((current) => ({
        ...current,
        phases: newPhases,
      }))
      showToast('Fase reordenada')
      return
    }

    if (type === 'TASK') {
      // Reorder tasks within or between phases
      const sourcePhaseIndex = parseInt(source.droppableId)
      const destinationPhaseIndex = parseInt(destination.droppableId)

      const newPhases = plan.phases.map((phase) => ({
        ...phase,
        tasks: [...phase.tasks],
      }))

      const sourcePhase = newPhases[sourcePhaseIndex]
      const [removedTask] = sourcePhase.tasks.splice(source.index, 1)

      if (sourcePhaseIndex === destinationPhaseIndex) {
        // Same phase, just reorder
        sourcePhase.tasks.splice(destination.index, 0, removedTask)
      } else {
        // Different phase, move task
        const destinationPhase = newPhases[destinationPhaseIndex]
        destinationPhase.tasks.splice(destination.index, 0, removedTask)
      }

      setPlan((current) => ({
        ...current,
        phases: newPhases,
      }))
      showToast('Tarea reordenada')
    }
  }

  const handleExportPlan = async (format: 'text' | 'json' | 'csv' | 'markdown') => {
    let content: string
    let filename: string
    let mimeType: string

    switch (format) {
      case 'json':
        content = JSON.stringify(plan, null, 2)
        filename = `plan-${Date.now()}.json`
        mimeType = 'application/json'
        break
      case 'csv':
        const headers = ['Fase', 'Tarea', 'Duración', 'Prioridad', 'Fecha', 'Estado', 'Etiquetas']
        const rows = plan.phases.flatMap((phase) =>
          phase.tasks.map((task) => [
            phase.name,
            task.title,
            task.duration,
            task.priority,
            task.date,
            task.done ? 'Completada' : 'Pendiente',
            task.tags.join('; '),
          ])
        )
        content = [headers, ...rows].map((row) => row.join(',')).join('\n')
        filename = `plan-${Date.now()}.csv`
        mimeType = 'text/csv'
        break
      case 'markdown':
        content = `# Plan: ${plan.goal}\n\n**Duración:** ${plan.totalDuration}\n**Progreso:** ${progress}%\n\n${plan.phases.map((phase) => `## ${phase.name}\n${phase.description}\n\n### Tareas\n${phase.tasks.map((task) => `- [${task.done ? 'x' : ' '}] ${task.title} (${task.priority}, ${task.duration})${task.tags.length > 0 ? ` - Etiquetas: ${task.tags.join(', ')}` : ''}`).join('\n')}`).join('\n\n')}`
        filename = `plan-${Date.now()}.md`
        mimeType = 'text/markdown'
        break
      default:
        content = [
          `Meta: ${plan.goal}`,
          `Duración: ${plan.totalDuration}`,
          `Progreso: ${progress}%`,
          '',
          ...plan.phases.flatMap((phase) =>
            phase.tasks.map(
              (task) => `- ${phase.name}: ${task.title} (${task.priority}, ${task.done ? 'done' : 'pending'})`,
            ),
          ),
        ].join('\n')
        filename = `plan-${Date.now()}.txt`
        mimeType = 'text/plain'
    }

    try {
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      showToast(`Plan exportado como ${format.toUpperCase()}`)
    } catch {
      showToast('No se pudo exportar el plan')
    }
  }

  if (isSessionLoading) {
    return (
      <main className="app-loader" aria-busy="true" aria-live="polite">
        <div className="loader-mark">P</div>
        <div className="loader-spinner" aria-hidden="true" />
        <p>Preparando tu espacio de trabajo</p>
      </main>
    )
  }

  if (!session && view === 'landing') {
    return (
      <main className="landing-page">
        <section className="landing-hero">
          <nav className="landing-nav" aria-label="Navegacion principal">
            <div className="brand-wrap">
              <div className="brand-mark">P</div>
              <h1>PlanBot</h1>
            </div>
            <button className="nav-login" type="button" onClick={() => setView('auth')}>
              Entrar
            </button>
          </nav>

          <div className="hero-content">
            <p className="hero-kicker">Tu siguiente avance empieza hoy</p>
            <h2>PlanBot</h2>
            <p className="hero-copy">
              Convierte una meta ambiciosa en un plan diario que puedes terminar.
            </p>
            <div className="hero-actions">
              <button
                className="hero-primary"
                type="button"
                onClick={() => {
                  setAuthMode('register')
                  setView('auth')
                }}
              >
                Crear mi plan
              </button>
              <a className="hero-secondary" href="#como-funciona">Ver como funciona</a>
            </div>
          </div>
        </section>

        <section id="como-funciona" className="landing-flow">
          <div>
            <p className="landing-label">Un sistema para avanzar</p>
            <h2>De la idea a la proxima tarea, sin perder el rumbo.</h2>
          </div>
          <ol className="flow-steps">
            <li><span>01</span><strong>Describe tu meta</strong><p>Cuenta lo que quieres lograr y el tiempo que tienes.</p></li>
            <li><span>02</span><strong>Recibe tu plan</strong><p>La IA organiza etapas, prioridades y tareas concretas.</p></li>
            <li><span>03</span><strong>Mantente en marcha</strong><p>Marca avances y ajusta el plan cuando tu contexto cambie.</p></li>
          </ol>
        </section>

        <section className="landing-cta">
          <p className="landing-label">Listo para empezar</p>
          <h2>Tu objetivo merece un plan claro.</h2>
          <button
            className="hero-primary"
            type="button"
            onClick={() => {
              setAuthMode('register')
              setView('auth')
            }}
          >
            Crear una cuenta
          </button>
        </section>
      </main>
    )
  }

  if (!session) {
    return (
      <main className={isLightTheme ? 'auth-page light-theme' : 'auth-page'}>
        <section className="auth-panel">
          <button
            className="theme-toggle"
            type="button"
            aria-label="Cambiar tema"
            onClick={() => setIsLightTheme((current) => !current)}
          >
            {isLightTheme ? 'Modo oscuro' : 'Modo claro'}
          </button>
          {isAuthenticating && (
            <div className="auth-loader" role="status" aria-live="polite">
              <span className="loader-spinner" aria-hidden="true" />
              <span>Conectando de forma segura...</span>
            </div>
          )}
          <p className="auth-eyebrow">Planificador inteligente</p>
          <div className="auth-brand">
            <div className="auth-logo">P</div>
            <h1>PlanBot</h1>
          </div>
          <h2>
            {authMode === 'login'
              ? 'Continua tu plan'
              : authMode === 'register' ? 'Crea tu espacio' : 'Recupera tu acceso'}
          </h2>
          <button className="back-link" type="button" onClick={() => setView('landing')}>
            Volver al inicio
          </button>
          <form className="auth-form" onSubmit={handleAuthentication}>
            <label>
              Correo
              <span className="input-with-icon">
                <span aria-hidden="true">@</span>
                <input
                  type="email"
                  value={authEmail}
                  onChange={(event) => setAuthEmail(event.target.value)}
                  placeholder="tu@email.com"
                  autoComplete="email"
                  required
                />
              </span>
            </label>
            {authMode !== 'forgot' && (
              <label>
                Contrasena
                <span className="password-field">
                  <span className="password-icon" aria-hidden="true">*</span>
                  <input
                    type={isPasswordVisible ? 'text' : 'password'}
                    value={authPassword}
                    onChange={(event) => setAuthPassword(event.target.value)}
                    placeholder="********"
                    autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                    minLength={8}
                    required
                  />
                  <button
                    className="password-toggle"
                    type="button"
                    onClick={() => setIsPasswordVisible((visible) => !visible)}
                  >
                    {isPasswordVisible ? 'Ocultar' : 'Mostrar'}
                  </button>
                </span>
                {authMode === 'register' && <small>Minimo 8 caracteres.</small>}
              </label>
            )}
            {authMessage && <p className="auth-message">{authMessage}</p>}
            <button className="primary-button" type="submit" disabled={isAuthenticating}>
              {isAuthenticating
                ? 'Procesando...'
                : authMode === 'login'
                  ? 'Iniciar sesion'
                  : authMode === 'register' ? 'Crear cuenta' : 'Enviar enlace'}
            </button>
          </form>
          {authMode !== 'forgot' && (
            <button className="auth-switch" type="button" onClick={() => void handleMagicLink()}>
              Acceder con enlace magico
            </button>
          )}
          <div className="auth-divider">o continua con</div>
          <button className="oauth-button" type="button" onClick={() => void handleGoogleSignIn()}>
            <span className="google-mark" aria-hidden="true">G</span>Continuar con Google
          </button>
          <div className="auth-links">
            <button className="auth-switch" type="button" onClick={() => setAuthMode('forgot')}>
              Olvide mi contrasena
            </button>
            <button
              className="auth-switch"
              type="button"
              onClick={() => setAuthMode(authMode === 'register' ? 'login' : 'register')}
            >
              {authMode === 'register' ? 'Ya tengo una cuenta' : 'Crear una cuenta'}
            </button>
          </div>
        </section>
      </main>
    )
  }

  return (
    <div className="page-shell">
      <header className="topbar">
        <div className="brand-wrap">
          <div className="brand-mark">P</div>
          <div>
            <p className="eyebrow">Planificador inteligente</p>
            <h1>PlanBot</h1>
          </div>
        </div>

        <div className="header-actions">
          <button type="button" className="ghost-button" onClick={() => setShowStatistics(!showStatistics)}>
            {showStatistics ? 'Ocultar estadísticas' : 'Ver estadísticas'}
          </button>
          <button type="button" className="ghost-button" onClick={() => void supabase.auth.signOut()}>
            Cerrar sesion
          </button>
          <button type="button" className="ghost-button" onClick={handleReset}>
            Resetear
          </button>
          <button type="button" className="ghost-button" onClick={handleApprove}>
            {approved ? 'Plan aprobado' : 'Aprobar plan'}
          </button>
        </div>
      </header>

      <main className="main-grid">
        <section className="panel input-panel">
          <p className="section-label">Tu meta</p>
          <textarea
            value={goal}
            onChange={(event) => setGoal(event.target.value)}
            rows={4}
            placeholder="Ejemplo: Quiero lanzar mi curso en 30 días"
          />

          <div className="button-row">
            <button type="button" className="primary-button" onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? 'Creando plan...' : 'Generar plan'}
            </button>
            <div className="export-menu-container">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowExportMenu(!showExportMenu)}
              >
                Exportar ▼
              </button>
              {showExportMenu && (
                <div className="export-menu">
                  <button type="button" onClick={() => { handleExportPlan('text'); setShowExportMenu(false) }}>
                    📄 Texto
                  </button>
                  <button type="button" onClick={() => { handleExportPlan('json'); setShowExportMenu(false) }}>
                    📋 JSON
                  </button>
                  <button type="button" onClick={() => { handleExportPlan('csv'); setShowExportMenu(false) }}>
                    📊 CSV
                  </button>
                  <button type="button" onClick={() => { handleExportPlan('markdown'); setShowExportMenu(false) }}>
                    📝 Markdown
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="mode-box">
            <p className="tips-title">Recordatorios</p>
            <div className="mode-options">
              {(['Diario', 'Semanal', 'Personalizado'] as ReminderMode[]).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  className={mode === reminderMode ? 'mode-option active' : 'mode-option'}
                  onClick={() => {
                    setReminderMode(mode)
                    setPlan((current) => ({
                      ...current,
                      nextReminder: getReminderText(mode, current.goal),
                    }))
                  }}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <div className="info-box">
            <p className="tips-title">PlanBot te ayuda a</p>
            <ul>
              <li>Desglosar la meta</li>
              <li>Definir tareas por prioridad</li>
              <li>Marcar el orden correcto</li>
              <li>Recordar fechas clave</li>
            </ul>
          </div>
        </section>

        <section className="panel overview-panel">
          <div className="goal-header">
            <div>
              <p className="section-label">Objetivo</p>
              <h2>{plan.goal}</h2>
            </div>
            <span className="pill">{plan.totalDuration}</span>
          </div>

          <div className="stats-grid">
            <div className="stat-card accent">
              <span>Progreso</span>
              <strong>{progress}%</strong>
            </div>
            <div className="stat-card">
              <span>Tareas</span>
              <strong>{totalTasks}</strong>
            </div>
            <div className="stat-card">
              <span>Completadas</span>
              <strong>{completedTasks}</strong>
            </div>
          </div>

          <div className="progress-block">
            <div className="progress-labels">
              <span>Avance del plan</span>
              <span>{progress}%</span>
            </div>
            <div className="progress-bar">
              <span style={{ width: `${progress}%` }} />
            </div>
          </div>

          <div className="reminder-box">
            <p className="section-label">Siguiente recordatorio</p>
            <strong>{plan.nextReminder}</strong>
          </div>

          <div className={`status-badge ${approved ? 'approved' : 'draft'}`}>
            {approved ? 'Plan aprobado' : 'Borrador en edición'}
          </div>

          <div className="filter-row">
            <label htmlFor="filterSelect">Filtrar tareas</label>
            <select
              id="filterSelect"
              value={taskFilter}
              onChange={(event) => setTaskFilter(event.target.value as TaskFilter)}
            >
              <option value="all">Todas</option>
              <option value="pending">Pendientes</option>
              <option value="done">Completadas</option>
            </select>
          </div>

          <div className="advanced-filters">
            <div className="search-box">
              <input
                type="text"
                placeholder="Buscar tareas..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
              />
            </div>
            
            <div className="filter-group">
              <label htmlFor="priorityFilter">Prioridad</label>
              <select
                id="priorityFilter"
                value={priorityFilter}
                onChange={(event) => setPriorityFilter(event.target.value as PriorityFilter)}
              >
                <option value="all">Todas</option>
                <option value="Alta">Alta</option>
                <option value="Media">Media</option>
                <option value="Baja">Baja</option>
              </select>
            </div>
            
            <div className="filter-group">
              <label htmlFor="dateFilter">Fecha</label>
              <select
                id="dateFilter"
                value={dateFilter}
                onChange={(event) => setDateFilter(event.target.value as DateFilter)}
              >
                <option value="all">Todas</option>
                <option value="today">Hoy</option>
                <option value="week">Esta semana</option>
                <option value="month">Este mes</option>
              </select>
            </div>
          </div>
        </section>
      </main>

      {showStatistics && (
        <section className="statistics-panel panel">
          <div className="statistics-header">
            <p className="section-label">Análisis de rendimiento</p>
            <h3>Estadísticas detalladas</h3>
          </div>

          <div className="statistics-grid">
            <div className="stat-card-lg">
              <span className="stat-label">Planes creados</span>
              <strong className="stat-value">{statistics.totalPlans}</strong>
              <div className="stat-indicator">Total histórico</div>
            </div>
            
            <div className="stat-card-lg accent">
              <span className="stat-label">Tareas completadas</span>
              <strong className="stat-value">{statistics.completedTasks}</strong>
              <div className="stat-indicator">De {statistics.totalTasks} totales</div>
            </div>
            
            <div className="stat-card-lg">
              <span className="stat-label">Progreso promedio</span>
              <strong className="stat-value">{statistics.averageProgress}%</strong>
              <div className="stat-indicator">Todos los planes</div>
            </div>
            
            <div className="stat-card-lg">
              <span className="stat-label">Tareas de alta prioridad</span>
              <strong className="stat-value">{statistics.highPriorityTasks}</strong>
              <div className="stat-indicator">Requieren atención</div>
            </div>
            
            <div className="stat-card-lg">
              <span className="stat-label">Completadas esta semana</span>
              <strong className="stat-value">{statistics.tasksThisWeek}</strong>
              <div className="stat-indicator">Últimos 7 días</div>
            </div>
            
            <div className="stat-card-lg">
              <span className="stat-label">Tasa de completación</span>
              <strong className="stat-value">{statistics.completionRate}%</strong>
              <div className="stat-indicator">Plan actual</div>
            </div>
          </div>

          <div className="statistics-chart">
            <h4>Distribución de progreso por fase</h4>
            <div className="phase-progress">
              {plan.phases.map((phase) => {
                const phaseTasks = phase.tasks.length
                const phaseCompleted = phase.tasks.filter((task) => task.done).length
                const phaseProgress = phaseTasks > 0 ? Math.round((phaseCompleted / phaseTasks) * 100) : 0
                
                return (
                  <div key={phase.id} className="phase-progress-item">
                    <div className="phase-progress-info">
                      <span className="phase-name">{phase.name}</span>
                      <span className="phase-percentage">{phaseProgress}%</span>
                    </div>
                    <div className="phase-progress-bar">
                      <div 
                        className="phase-progress-fill" 
                        style={{ width: `${phaseProgress}%` }}
                      />
                    </div>
                    <div className="phase-progress-details">
                      <span>{phaseCompleted} de {phaseTasks} tareas</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </section>
      )}

      <section className="history-panel panel">
        <div className="history-header">
          <p className="section-label">Historial</p>
          <h3>Planes guardados</h3>
        </div>

        <div className="history-list">
          {history.length === 0 ? (
            <p className="empty-history">Aún no tienes planes guardados.</p>
          ) : (
            history.map((entry) => (
              <button type="button" key={entry.id} className="history-item" onClick={() => handleHistorySelect(entry)}>
                <div>
                  <strong>{entry.goal}</strong>
                  <span>{entry.createdAt}</span>
                </div>
                <small>{entry.progress}% • {entry.totalDuration}</small>
              </button>
            ))
          )}
        </div>
      </section>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="phases" type="PHASE" direction="horizontal">
          {(provided) => (
            <section
              className="plan-panel"
              {...provided.droppableProps}
              ref={provided.innerRef}
            >
              {visiblePhases.map((phase, index) => (
                <Draggable key={phase.id} draggableId={phase.id} index={index}>
                  {(provided, snapshot) => (
                    <article
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      className={`phase-card ${snapshot.isDragging ? 'dragging' : ''}`}
                    >
                      <div className="phase-header" {...provided.dragHandleProps}>
                        <div>
                          <p className="section-label">Etapa</p>
                          <h3>{phase.name}</h3>
                        </div>
                        <span>{phase.duration}</span>
                      </div>

                      <p className="phase-description">{phase.description}</p>

                      <div className="add-task-box">
              <input
                type="text"
                placeholder="Añadir tarea"
                value={taskForms[phase.id]?.title ?? ''}
                onChange={(event) =>
                  setTaskForms((current) => ({
                    ...current,
                    [phase.id]: {
                      title: event.target.value,
                      duration: current[phase.id]?.duration ?? '1 día',
                      priority: current[phase.id]?.priority ?? 'Media',
                    },
                  }))
                }
              />
              <div className="mini-form-row">
                <select
                  value={taskForms[phase.id]?.duration ?? '1 día'}
                  onChange={(event) =>
                    setTaskForms((current) => ({
                      ...current,
                      [phase.id]: {
                        title: current[phase.id]?.title ?? '',
                        duration: event.target.value,
                        priority: current[phase.id]?.priority ?? 'Media',
                      },
                    }))
                  }
                >
                  <option value="1 día">1 día</option>
                  <option value="2 días">2 días</option>
                  <option value="3 días">3 días</option>
                  <option value="1 semana">1 semana</option>
                </select>
                <select
                  value={taskForms[phase.id]?.priority ?? 'Media'}
                  onChange={(event) =>
                    setTaskForms((current) => ({
                      ...current,
                      [phase.id]: {
                        title: current[phase.id]?.title ?? '',
                        duration: current[phase.id]?.duration ?? '1 día',
                        priority: event.target.value as Priority,
                      },
                    }))
                  }
                >
                  <option value="Alta">Alta</option>
                  <option value="Media">Media</option>
                  <option value="Baja">Baja</option>
                </select>
                <button type="button" className="mini-add-button" onClick={() => handleAddTask(phase.id)}>
                  Añadir
                </button>
              </div>
              <div className="tag-input-row">
                <input
                  type="text"
                  placeholder="Etiquetas (separadas por comas)"
                  value={tagInput[phase.id] ?? ''}
                  onChange={(event) =>
                    setTagInput((current) => ({
                      ...current,
                      [phase.id]: event.target.value,
                    }))
                  }
                />
                {availableTags.length > 0 && (
                  <div className="available-tags">
                    <span className="tag-label">Etiquetas disponibles:</span>
                    {availableTags.slice(0, 5).map((tag) => (
                      <button
                        key={tag}
                        type="button"
                        className="tag-suggestion"
                        onClick={() => {
                          const currentTags = tagInput[phase.id] || ''
                          const newTags = currentTags ? `${currentTags}, ${tag}` : tag
                          setTagInput((current) => ({
                            ...current,
                            [phase.id]: newTags,
                          }))
                        }}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              </div>

                      <Droppable droppableId={plan.phases.findIndex(p => p.id === phase.id).toString()} type="TASK">
                        {(provided) => (
                          <div className="task-list" ref={provided.innerRef} {...provided.droppableProps}>
                            {phase.tasks.length === 0 ? (
                              <p className="empty-phase">No hay tareas en este filtro.</p>
                            ) : (
                              phase.tasks.map((task, taskIndex) => (
                                <Draggable key={task.id} draggableId={task.id} index={taskIndex}>
                                  {(provided, snapshot) => (
                                    <div
                                      ref={provided.innerRef}
                                      {...provided.draggableProps}
                                      {...provided.dragHandleProps}
                                      className={`task-item ${task.done ? 'done' : ''} ${snapshot.isDragging ? 'dragging' : ''}`}
                                    >
                    <button
                      type="button"
                      className="task-toggle"
                      onClick={() => handleTaskToggle(task.id)}
                      aria-label={task.done ? 'Marcar como pendiente' : 'Marcar como completada'}
                    >
                      <span>{task.done ? '✓' : ''}</span>
                    </button>

                    <div className="task-copy">
                      <div className="task-topline">
                        <h4>{task.title}</h4>
                        <span className={`priority priority-${task.priority.toLowerCase()}`}>
                          {task.priority}
                        </span>
                      </div>

                      <div className="task-meta">
                        <span>{task.duration}</span>
                        <span>•</span>
                        <span>{task.date}</span>
                      </div>

                      {task.tags.length > 0 && (
                        <div className="task-tags">
                          {task.tags.map((tag) => (
                            <span key={tag} className="task-tag">
                              {tag}
                              <button
                                type="button"
                                className="tag-remove"
                                onClick={() => handleRemoveTag(phase.id, task.id, tag)}
                              >
                                ×
                              </button>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                                    <button
                                      type="button"
                                      className="delete-task-button"
                                      onClick={() => handleDeleteTask(phase.id, task.id)}
                                      aria-label={`Eliminar tarea ${task.title}`}
                                    >
                                      ×
                                    </button>
                                  </div>
                                )}
                              </Draggable>
                            ))
                          )}
                          {provided.placeholder}
                        </div>
                      )}
                    </Droppable>
                    </article>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </section>
          )}
        </Droppable>
      </DragDropContext>

      {toast && <div className="toast">{toast}</div>}
    </div>
  )
}

export type { Priority, TaskFilter, ReminderMode, DateFilter, Task, Phase, Plan, HistoryEntry, TaskFormState, Statistics }
export default App
