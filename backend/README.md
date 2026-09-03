# Sistema Backend Autónomo Controlado

Sistema de backend inteligente con autonomía limitada y controles de seguridad para el proyecto AutoPlan.

## 🎯 Características

### ✅ Autonomía Controlada
- Toma de decisiones autónoma dentro de límites predefinidos
- Niveles de autonomía configurables (low, medium, high)
- Límite de acciones autónomas antes de requerir aprobación
- Tiempo límite para acciones individuales

### 🧠 Motor de Decisiones
- Evaluación de múltiples alternativas
- Cálculo de confianza para cada opción
- Aprendizaje de decisiones pasadas
- Generación de razonamiento explicativo

### 🛡️ Sistema de Seguridad
- Reglas de seguridad configurables
- Monitoreo de uso de recursos
- Detección de patrones anómalos
- Parada de emergencia automática
- Verificación de acceso a datos sensibles

### 👤 Control Humano
- Aprobación/rechazo de acciones
- Inicio/detención del sistema
- Monitoreo en tiempo real
- Intervención manual cuando necesario

## 📁 Estructura del Sistema

```
backend/
├── autonomous-agent.ts    # Agente autónomo principal
├── decision-engine.ts     # Motor de toma de decisiones
├── safety-monitor.ts      # Sistema de monitoreo y seguridad
├── index.ts              # Integración principal
├── example-usage.ts      # Ejemplos de uso
└── README.md             # Este archivo
```

## 🚀 Uso Básico

### 1. Iniciar el Sistema

```typescript
import { AutonomousAPI } from './index';

// Iniciar con un controlador humano
await AutonomousAPI.start('human-controller-id');
```

### 2. Procesar Solicitudes

```typescript
const result = await AutonomousAPI.processRequest({
  type: 'generate_plan',
  data: { goal: 'Aprender React en 2 semanas' },
  urgency: 'low'
});

if (result.success) {
  console.log('Acción completada:', result.result);
} else if (result.requiresHumanApproval) {
  console.log('Requiere aprobación humana');
  // Aprobar o rechazar
}
```

### 3. Monitorear Estado

```typescript
const status = AutonomousAPI.getStatus();
console.log('Estado del sistema:', status);
```

### 4. Controlar Acciones

```typescript
// Aprobar acción pendiente
await AutonomousAPI.approveAction('action-id', 'controller-id');

// Rechazar acción pendiente
await AutonomousAPI.rejectAction('action-id', 'controller-id');
```

### 5. Detener el Sistema

```typescript
await AutonomousAPI.stop('controller-id');
```

## 🔧 Configuración

### Configuración del Agente

```typescript
const agentConfig: AutonomousAgentConfig = {
  autonomyLevel: 'medium',           // Nivel de autonomía
  maxAutonomousActions: 50,         // Máximo de acciones autónomas
  actionTimeLimit: 30,              // Límite de tiempo por acción (segundos)
  humanApprovalRequired: true,       // Requiere aprobación humana
  monitoringEnabled: true,           // Monitoreo activado
  emergencyStop: true,              // Parada de emergencia disponible
  maxResourceUsage: 80,             // Límite de recursos (%)
  allowedActions: [                  // Acciones permitidas
    'generate_plan',
    'optimize_tasks',
    'send_reminder'
  ],
  forbiddenActions: [                // Acciones prohibidas
    'delete_user_data',
    'modify_system_config'
  ]
};
```

### Reglas de Seguridad Personalizadas

```typescript
import { safetyMonitor } from './safety-monitor';

const customRule: SafetyRule = {
  id: 'custom_rule',
  name: 'Regla Personalizada',
  description: 'Descripción de la regla',
  check: (action) => {
    // Lógica de verificación
    return true; // o false
  },
  severity: 'warning',
  action: 'warn'
};

safetyMonitor.addSafetyRule(customRule);
```

## 📊 Ejemplos de Integración

### Generación Autónoma de Planes

```typescript
const planRequest = {
  type: 'generate_plan',
  data: {
    goal: 'Lanzar curso en 30 días',
    preferences: {
      intensity: 'high',
      focus: 'practical'
    }
  },
  urgency: 'medium'
};

const result = await AutonomousAPI.processRequest(planRequest);
```

### Optimización de Tareas

```typescript
const optimizeRequest = {
  type: 'optimize_tasks',
  data: {
    projectId: 'project-123',
    optimizationGoal: 'efficiency'
  },
  urgency: 'low'
};

const result = await AutonomousAPI.processRequest(optimizeRequest);
```

### Análisis de Progreso

```typescript
const analysisRequest = {
  type: 'analyze_progress',
  data: {
    userId: 'user-123',
    timeframe: 'weekly'
  },
  urgency: 'low'
};

const result = await AutonomousAPI.processRequest(analysisRequest);
```

## 🛡️ Mecanismos de Seguridad

### 1. Límites de Recursos
- CPU: 80% máximo
- Memoria: 75% máximo
- Red: 60% máximo
- Disco: 50% máximo

### 2. Reglas de Seguridad Activas
- ✅ Límite de uso de recursos
- ✅ Detección de acciones de alto riesgo
- ✅ Detección de patrones inusuales
- ✅ Monitoreo de acceso a datos sensibles
- ✅ Detección de acciones rápidas

### 3. Niveles de Riesgo
- **Low**: Ejecución autónoma permitida
- **Medium**: Requiere evaluación adicional
- **High**: Siempre requiere aprobación humana

### 4. Parada de Emergencia
- Activación manual
- Activación automática (3+ eventos críticos)
- Bloqueo inmediato de todas las acciones

## 📈 Monitoreo y Logs

### Estado del Sistema

```typescript
const status = AutonomousAPI.getStatus();
// Incluye:
// - Estado de actividad
// - Estadísticas del agente
// - Estadísticas de decisiones
// - Estado de seguridad
// - Logs recientes
```

### Logs del Sistema

Todos las acciones y decisiones son registradas automáticamente:
- Timestamp de cada acción
- Razonamiento de decisiones
- Resultados de verificaciones de seguridad
- Estados de recursos

## ⚠️ Limitaciones de Seguridad

Este sistema **NO** es:
- ❌ Una AGI (Inteligencia Artificial General)
- ❌ Un sistema con conciencia real
- ❌ Completamente autónomo sin límites
- ❌ Capaz de aprender sin supervisión

Este sistema **SÍ** es:
- ✅ Un backend inteligente con autonomía limitada
- ✅ Controlado por reglas y límites predefinidos
- ✅ Supervisado por humanos
- ✅ Con mecanismos de seguridad múltiples
- ✅ Transparente en sus decisiones
- ✅ Con capacidad de intervención humana

## 🔮 Futuras Mejoras

- [ ] Integración con ML para mejor toma de decisiones
- [ ] Sistema de aprendizaje más sofisticado
- [ ] Interfaz web para control humano
- [ ] Alertas en tiempo real
- [ ] Sistema de backup y recuperación
- [ ] Integración con más servicios de AutoPlan

## 📝 Notas Importantes

1. **Siempre requiere control humano**: El sistema no debe operar sin supervisión
2. **Configuración adecuada**: Ajustar límites según el caso de uso
3. **Monitoreo constante**: Revisar logs y estado regularmente
4. **Actualización de reglas**: Mantener reglas de seguridad actualizadas
5. **Testing exhaustivo**: Probar el sistema antes de producción

## 🆘 Soporte

Para problemas o preguntas sobre el sistema autónomo:
1. Revisar los logs del sistema
2. Verificar el estado de seguridad
3. Consultar la documentación de cada componente
4. Contactar al equipo de desarrollo

---

**⚠️ Advertencia**: Este sistema es una herramienta de automatización con controles de seguridad. No debe considerarse como una AGI ni sistema con inteligencia general. Siempre requiere supervisión humana adecuada.