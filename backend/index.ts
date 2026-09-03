/**
 * Sistema Backend Autónomo Controlado - Integración Principal
 * 
 * Este archivo integra todos los componentes del sistema autónomo:
 * - Agente autónomo con límites
 * - Motor de toma de decisiones
 * - Monitor de seguridad
 * - Sistema de control humano
 */

import { autonomousAgent, AutonomousAgentConfig, Action } from './autonomous-agent';
import { decisionEngine, DecisionContext, DecisionOption } from './decision-engine';
import { safetyMonitor, SafetyRule } from './safety-monitor';

/**
 * Sistema Principal Autónomo Controlado
 */
class ControlledAutonomousSystem {
  private isActive: boolean = false;
  private humanController: string | null = null;
  private systemLogs: string[] = [];

  /**
   * Inicia el sistema autónomo
   */
  async start(controllerId: string): Promise<void> {
    this.humanController = controllerId;
    this.isActive = true;
    this.log(`System started by human controller: ${controllerId}`);
    console.log('[SYSTEM] Autonomous system started with safety controls');
  }

  /**
   * Detiene el sistema autónomo
   */
  async stop(controllerId: string): Promise<void> {
    if (this.humanController !== controllerId) {
      throw new Error('Unauthorized: Only the controller can stop the system');
    }

    this.isActive = false;
    autonomousAgent.triggerEmergencyStop();
    this.log(`System stopped by human controller: ${controllerId}`);
    console.log('[SYSTEM] Autonomous system stopped');
  }

  /**
   * Procesa una solicitud autónoma
   */
  async processRequest(request: {
    type: string;
    data: Record<string, any>;
    urgency?: 'low' | 'medium' | 'high';
  }): Promise<{
    success: boolean;
    result: any;
    decision?: any;
    safetyCheck?: any;
    requiresHumanApproval: boolean;
  }> {
    if (!this.isActive) {
      return {
        success: false,
        result: null,
        requiresHumanApproval: true
      };
    }

    this.log(`Processing request: ${request.type}`);

    try {
      // 1. Crear contexto de decisión
      const context: DecisionContext = {
        situation: request.type,
        data: request.data,
        urgency: request.urgency || 'medium',
        confidence: 0.8,
        alternatives: this.generateAlternatives(request)
      };

      // 2. Motor de toma de decisiones
      const decision = await decisionEngine.makeDecision(context);

      // 3. Verificación de seguridad
      const action: Action = {
        id: `action-${Date.now()}`,
        type: decision.selectedOption.action,
        description: decision.selectedOption.description,
        parameters: request.data,
        requiresApproval: decision.requiresHumanApproval,
        riskLevel: decision.selectedOption.riskLevel,
        timestamp: new Date()
      };

      const safetyCheck = await safetyMonitor.monitorAction(action);

      if (!safetyCheck.allowed) {
        this.log(`Action blocked by safety monitor: ${safetyCheck.criticals.join(', ')}`);
        return {
          success: false,
          result: null,
          decision,
          safetyCheck,
          requiresHumanApproval: true
        };
      }

      // 4. Ejecutar acción si pasa seguridad
      if (decision.requiresHumanApproval) {
        this.log(`Action requires human approval: ${action.type}`);
        return {
          success: false,
          result: null,
          decision,
          safetyCheck,
          requiresHumanApproval: true
        };
      }

      const result = await autonomousAgent.executeAction(action);

      this.log(`Action completed successfully: ${action.type}`);
      return {
        success: result.success,
        result: result.result,
        decision,
        safetyCheck,
        requiresHumanApproval: false
      };

    } catch (error) {
      this.log(`Error processing request: ${error}`);
      return {
        success: false,
        result: null,
        requiresHumanApproval: true
      };
    }
  }

  /**
   * Genera alternativas para una solicitud
   */
  private generateAlternatives(request: any): DecisionOption[] {
    // Generar alternativas basadas en el tipo de solicitud
    switch (request.type) {
      case 'generate_plan':
        return [
          {
            action: 'generate_plan',
            description: 'Generar plan automáticamente',
            riskLevel: 'low',
            expectedOutcome: 'Plan generado con IA',
            confidence: 0.85
          },
          {
            action: 'request_human_input',
            description: 'Solicitar input humano',
            riskLevel: 'low',
            expectedOutcome: 'Plan basado en input humano',
            confidence: 0.95
          }
        ];
      case 'optimize_tasks':
        return [
          {
            action: 'optimize_tasks',
            description: 'Optimizar tareas automáticamente',
            riskLevel: 'medium',
            expectedOutcome: 'Tareas reorganizadas',
            confidence: 0.75
          },
          {
            action: 'suggest_optimizations',
            description: 'Sugerir optimizaciones',
            riskLevel: 'low',
            expectedOutcome: 'Sugerencias presentadas',
            confidence: 0.90
          }
        ];
      default:
        return [
          {
            action: 'proceed_autonomously',
            description: 'Proceder autónomamente',
            riskLevel: 'medium',
            expectedOutcome: 'Acción completada',
            confidence: 0.70
          },
          {
            action: 'request_approval',
            description: 'Solicitar aprobación',
            riskLevel: 'low',
            expectedOutcome: 'Esperar aprobación',
            confidence: 0.95
          }
        ];
    }
  }

  /**
   * Obtiene estado completo del sistema
   */
  getSystemStatus(): {
    isActive: boolean;
    controller: string | null;
    agentStatus: any;
    decisionStats: any;
    safetyStatus: any;
    recentLogs: string[];
  } {
    return {
      isActive: this.isActive,
      controller: this.humanController,
      agentStatus: autonomousAgent.getStatus(),
      decisionStats: decisionEngine.getDecisionStats(),
      safetyStatus: safetyMonitor.getSafetyStatus(),
      recentLogs: this.systemLogs.slice(-20)
    };
  }

  /**
   * Aprobación humana de acción pendiente
   */
  async approveAction(actionId: string, controllerId: string): Promise<boolean> {
    if (this.humanController !== controllerId) {
      throw new Error('Unauthorized');
    }

    this.log(`Action approved by human: ${actionId}`);
    return true;
  }

  /**
   * Rechazo humano de acción pendiente
   */
  async rejectAction(actionId: string, controllerId: string): Promise<boolean> {
    if (this.humanController !== controllerId) {
      throw new Error('Unauthorized');
    }

    this.log(`Action rejected by human: ${actionId}`);
    return true;
  }

  /**
   * Sistema de logging
   */
  private log(message: string): void {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}`;
    this.systemLogs.push(logEntry);
    console.log(logEntry);
  }

  /**
   * Actualizar configuración del sistema
   */
  updateConfig(newConfig: Partial<AutonomousAgentConfig>): void {
    // Aquí se implementaría la lógica para actualizar configuración
    this.log('System configuration updated');
  }
}

// Instancia del sistema principal
const autonomousSystem = new ControlledAutonomousSystem();

/**
 * API del sistema autónomo
 */
export const AutonomousAPI = {
  // Control del sistema
  start: (controllerId: string) => autonomousSystem.start(controllerId),
  stop: (controllerId: string) => autonomousSystem.stop(controllerId),
  
  // Procesamiento de solicitudes
  processRequest: (request: any) => autonomousSystem.processRequest(request),
  
  // Estado y monitoreo
  getStatus: () => autonomousSystem.getSystemStatus(),
  
  // Control humano
  approveAction: (actionId: string, controllerId: string) => 
    autonomousSystem.approveAction(actionId, controllerId),
  rejectAction: (actionId: string, controllerId: string) => 
    autonomousSystem.rejectAction(actionId, controllerId),
  
  // Configuración
  updateConfig: (config: any) => autonomousSystem.updateConfig(config)
};

export { ControlledAutonomousSystem, autonomousSystem };