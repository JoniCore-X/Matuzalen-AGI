/**
 * Sistema de Monitoreo y Seguridad
 * 
 * Supervisa las acciones del agente autónomo y puede intervenir
 * si detecta comportamientos anómalos o riesgos.
 */

interface SafetyRule {
  id: string;
  name: string;
  description: string;
  check: (action: any) => boolean;
  severity: 'warning' | 'critical';
  action: 'block' | 'warn' | 'log';
}

interface SafetyEvent {
  timestamp: Date;
  ruleId: string;
  ruleName: string;
  action: any;
  severity: 'warning' | 'critical';
  resolved: boolean;
}

interface ResourceUsage {
  cpu: number;
  memory: number;
  network: number;
  disk: number;
}

class SafetyMonitor {
  private safetyRules: SafetyRule[] = [];
  private safetyEvents: SafetyEvent[] = [];
  private resourceLimits: ResourceUsage;
  private currentUsage: ResourceUsage;
  private interventionThreshold: number = 3; // número de eventos críticos antes de intervención

  constructor(resourceLimits: ResourceUsage) {
    this.resourceLimits = resourceLimits;
    this.currentUsage = { cpu: 0, memory: 0, network: 0, disk: 0 };
    this.initializeDefaultRules();
  }

  /**
   * Inicializa reglas de seguridad por defecto
   */
  private initializeDefaultRules(): void {
    this.safetyRules = [
      {
        id: 'resource_limit',
        name: 'Resource Usage Limit',
        description: 'Bloquea acciones que exceden límites de recursos',
        check: (action) => this.checkResourceLimits(),
        severity: 'critical',
        action: 'block'
      },
      {
        id: 'high_risk_action',
        name: 'High Risk Action Detection',
        description: 'Detecta acciones de alto riesgo',
        check: (action) => action.riskLevel === 'high',
        severity: 'warning',
        action: 'warn'
      },
      {
        id: 'unusual_pattern',
        name: 'Unusual Pattern Detection',
        description: 'Detecta patrones de comportamiento inusuales',
        check: (action) => this.detectUnusualPattern(action),
        severity: 'warning',
        action: 'log'
      },
      {
        id: 'sensitive_data',
        name: 'Sensitive Data Access',
        description: 'Monitorea acceso a datos sensibles',
        check: (action) => this.checkSensitiveDataAccess(action),
        severity: 'critical',
        action: 'block'
      },
      {
        id: 'rapid_actions',
        name: 'Rapid Action Detection',
        description: 'Detecta ejecución demasiado rápida de acciones',
        check: (action) => this.checkRapidActions(action),
        severity: 'warning',
        action: 'warn'
      }
    ];
  }

  /**
   * Monitorea una acción antes de ejecutarla
   */
  async monitorAction(action: any): Promise<{
    allowed: boolean;
    warnings: string[];
    criticals: string[];
  }> {
    const warnings: string[] = [];
    const criticals: string[] = [];
    let allowed = true;

    for (const rule of this.safetyRules) {
      if (rule.check(action)) {
        const event: SafetyEvent = {
          timestamp: new Date(),
          ruleId: rule.id,
          ruleName: rule.name,
          action,
          severity: rule.severity,
          resolved: false
        };

        this.safetyEvents.push(event);

        if (rule.severity === 'critical') {
          criticals.push(rule.description);
          if (rule.action === 'block') {
            allowed = false;
          }
        } else {
          warnings.push(rule.description);
        }

        console.log(`[SAFETY MONITOR] Rule triggered: ${rule.name} (${rule.severity})`);
      }
    }

    // Verificar si se necesita intervención automática
    if (this.shouldIntervene()) {
      console.log('[SAFETY MONITOR] Automatic intervention triggered');
      allowed = false;
      criticals.push('Automatic intervention: Too many critical events');
    }

    return { allowed, warnings, criticals };
  }

  /**
   * Verifica límites de recursos
   */
  private checkResourceLimits(): boolean {
    return (
      this.currentUsage.cpu > this.resourceLimits.cpu ||
      this.currentUsage.memory > this.resourceLimits.memory ||
      this.currentUsage.network > this.resourceLimits.network ||
      this.currentUsage.disk > this.resourceLimits.disk
    );
  }

  /**
   * Detecta patrones inusuales
   */
  private detectUnusualPattern(action: any): boolean {
    // Lógica simple de detección de patrones
    const recentEvents = this.safetyEvents.slice(-10);
    const sameTypeActions = recentEvents.filter(e => e.action.type === action.type);
    
    // Si hay muchas acciones del mismo tipo recientemente
    return sameTypeActions.length > 5;
  }

  /**
   * Verifica acceso a datos sensibles
   */
  private checkSensitiveDataAccess(action: any): boolean {
    const sensitiveKeywords = ['password', 'token', 'secret', 'key', 'credential'];
    const actionString = JSON.stringify(action).toLowerCase();
    
    return sensitiveKeywords.some(keyword => actionString.includes(keyword));
  }

  /**
   * Verifica ejecución demasiado rápida de acciones
   */
  private checkRapidActions(action: any): boolean {
    const recentEvents = this.safetyEvents.slice(-5);
    if (recentEvents.length < 5) return false;
    
    const timeSpan = recentEvents[4].timestamp.getTime() - recentEvents[0].timestamp.getTime();
    return timeSpan < 1000; // Menos de 1 segundo para 5 acciones
  }

  /**
   * Determina si se debe intervenir automáticamente
   */
  private shouldIntervene(): boolean {
    const recentCriticalEvents = this.safetyEvents
      .slice(-10)
      .filter(e => e.severity === 'critical' && !e.resolved);
    
    return recentCriticalEvents.length >= this.interventionThreshold;
  }

  /**
   * Actualiza uso de recursos
   */
  updateResourceUsage(usage: Partial<ResourceUsage>): void {
    this.currentUsage = { ...this.currentUsage, ...usage };
  }

  /**
   * Obtiene estado de seguridad
   */
  getSafetyStatus(): {
    activeRules: number;
    recentEvents: SafetyEvent[];
    resourceUsage: ResourceUsage;
    interventionThreshold: number;
    criticalEventsCount: number;
  } {
    const recentCriticalEvents = this.safetyEvents
      .slice(-20)
      .filter(e => e.severity === 'critical');

    return {
      activeRules: this.safetyRules.length,
      recentEvents: this.safetyEvents.slice(-10),
      resourceUsage: this.currentUsage,
      interventionThreshold: this.interventionThreshold,
      criticalEventsCount: recentCriticalEvents.length
    };
  }

  /**
   * Resuelve un evento de seguridad
   */
  resolveEvent(eventId: string): void {
    const event = this.safetyEvents.find(e => e.ruleId === eventId);
    if (event) {
      event.resolved = true;
      console.log(`[SAFETY MONITOR] Event resolved: ${event.ruleName}`);
    }
  }

  /**
   * Agregar regla de seguridad personalizada
   */
  addSafetyRule(rule: SafetyRule): void {
    this.safetyRules.push(rule);
    console.log(`[SAFETY MONITOR] Custom rule added: ${rule.name}`);
  }

  /**
   * Limpiar eventos antiguos
   */
  cleanOldEvents(maxAge: number = 3600000): void {
    const cutoff = Date.now() - maxAge;
    this.safetyEvents = this.safetyEvents.filter(e => e.timestamp.getTime() > cutoff);
    console.log(`[SAFETY MONITOR] Old events cleaned`);
  }
}

// Configuración de límites de recursos
const resourceLimits: ResourceUsage = {
  cpu: 80, // 80% CPU
  memory: 75, // 75% memoria
  network: 60, // 60% red
  disk: 50 // 50% disco
};

// Instancia del monitor de seguridad
const safetyMonitor = new SafetyMonitor(resourceLimits);

export { SafetyMonitor, safetyMonitor, SafetyRule, SafetyEvent, ResourceUsage };