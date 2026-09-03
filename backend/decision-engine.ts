/**
 * Motor de Toma de Decisiones - Interfaz de Alto Nivel
 * 
 * Este motor ahora actúa como interfaz con el núcleo cognitivo AGI.
 * Desacoplado de la lógica de decisión local, delega al servicio cognitivo.
 */

import { cognitiveClient, CognitiveRequest } from './cognitive-client';

interface DecisionContext {
  situation: string;
  data: Record<string, any>;
  urgency: 'low' | 'medium' | 'high';
  confidence: number;
  alternatives: DecisionOption[];
}

interface DecisionOption {
  action: string;
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
  expectedOutcome: string;
  confidence: number;
}

interface Decision {
  selectedOption: DecisionOption;
  reasoning: string;
  timestamp: Date;
  requiresHumanApproval: boolean;
  monitored: boolean;
}

class DecisionEngine {
  private decisionHistory: Decision[] = [];
  private learningPatterns: Map<string, number> = new Map();
  private safetyThreshold: number = 0.8;

  /**
   * Evalúa una situación y toma una decisión
   * Ahora delega al núcleo cognitivo AGI cuando está disponible
   */
  async makeDecision(context: DecisionContext): Promise<Decision> {
    // Verificar urgencia y confianza
    if (context.urgency === 'high' && context.confidence < this.safetyThreshold) {
      return this.createHighUrgencyDecision(context);
    }

    // Intentar usar el núcleo cognitivo AGI
    try {
      const cognitiveResponse = await cognitiveClient.processIntention({
        intention: context.situation,
        context: context.data,
        urgency: context.urgency,
        metadata: {
          alternatives: context.alternatives,
          confidence: context.confidence
        }
      });

      // Convertir respuesta cognitiva a decisión local
      const selectedOption = this.findMatchingOption(cognitiveResponse.decision, context.alternatives);
      
      const decision: Decision = {
        selectedOption: selectedOption || context.alternatives[0],
        reasoning: cognitiveResponse.reasoning,
        timestamp: new Date(),
        requiresHumanApproval: cognitiveResponse.requiresHumanApproval,
        monitored: true
      };
      
      this.decisionHistory.push(decision);
      this.learnFromDecision(decision, context);
      
      return decision;
    } catch (error) {
      console.warn('[DECISION ENGINE] Cognitive service unavailable, using local fallback');
      
      // Fallback a procesamiento local original
      return this.makeLocalDecision(context);
    }
  }

  /**
   * Procesamiento local de decisión (fallback)
   */
  private async makeLocalDecision(context: DecisionContext): Promise<Decision> {
    // Analizar opciones disponibles
    const evaluatedOptions = await this.evaluateOptions(context);
    
    // Seleccionar mejor opción
    const selectedOption = this.selectBestOption(evaluatedOptions);
    
    // Generar razonamiento
    const reasoning = this.generateReasoning(selectedOption, context);
    
    // Determinar si requiere aprobación humana
    const requiresApproval = this.determineApprovalNeed(selectedOption, context);
    
    // Registrar decisión
    const decision: Decision = {
      selectedOption,
      reasoning,
      timestamp: new Date(),
      requiresHumanApproval: requiresApproval,
      monitored: true
    };
    
    this.decisionHistory.push(decision);
    this.learnFromDecision(decision, context);
    
    return decision;
  }

  /**
   * Encuentra la opción que mejor coincide con la decisión cognitiva
   */
  private findMatchingOption(cognitiveDecision: string, alternatives: DecisionOption[]): DecisionOption | null {
    // Búsqueda simple por coincidencia de texto
    const matched = alternatives.find(opt => 
      opt.action.toLowerCase().includes(cognitiveDecision.toLowerCase()) ||
      cognitiveDecision.toLowerCase().includes(opt.action.toLowerCase())
    );
    
    return matched || null;
  }

  /**
   * Evalúa cada opción disponible
   */
  private async evaluateOptions(context: DecisionContext): Promise<DecisionOption[]> {
    return context.alternatives.map(option => ({
      ...option,
      confidence: this.calculateOptionConfidence(option, context)
    }));
  }

  /**
   * Calcula la confianza de una opción específica
   */
  private calculateOptionConfidence(option: DecisionOption, context: DecisionContext): number {
    let confidence = option.confidence;
    
    // Ajustar por nivel de riesgo
    if (option.riskLevel === 'high') {
      confidence *= 0.7;
    } else if (option.riskLevel === 'medium') {
      confidence *= 0.85;
    }
    
    // Ajustar por patrones aprendidos
    const patternKey = `${context.situation}_${option.action}`;
    const patternConfidence = this.learningPatterns.get(patternKey) || 0;
    confidence = (confidence + patternConfidence) / 2;
    
    return Math.min(confidence, 1.0);
  }

  /**
   * Selecciona la mejor opción basándose en múltiples factores
   */
  private selectBestOption(options: DecisionOption[]): DecisionOption {
    // Ordenar por confianza y nivel de riesgo
    const sortedOptions = options.sort((a, b) => {
      // Priorizar opciones de menor riesgo
      const riskScore = { high: 0, medium: 0.5, low: 1 };
      const riskComparison = riskScore[b.riskLevel] - riskScore[a.riskLevel];
      
      if (riskComparison !== 0) return riskComparison;
      
      // Si mismo nivel de riesgo, usar confianza
      return b.confidence - a.confidence;
    });
    
    return sortedOptions[0];
  }

  /**
   * Genera razonamiento explicativo
   */
  private generateReasoning(option: DecisionOption, context: DecisionContext): string {
    const factors = [
      `Situación: ${context.situation}`,
      `Urgencia: ${context.urgency}`,
      `Acción seleccionada: ${option.action}`,
      `Nivel de riesgo: ${option.riskLevel}`,
      `Confianza: ${(option.confidence * 100).toFixed(1)}%`,
      `Resultado esperado: ${option.expectedOutcome}`
    ];
    
    return factors.join(', ');
  }

  /**
   * Determina si la decisión requiere aprobación humana
   */
  private determineApprovalNeed(option: DecisionOption, context: DecisionContext): boolean {
    // Requiere aprobación si:
    // - Nivel de riesgo alto
    // - Confianza baja
    // - Urgencia alta con baja confianza
    return (
      option.riskLevel === 'high' ||
      option.confidence < this.safetyThreshold ||
      (context.urgency === 'high' && option.confidence < 0.9)
    );
  }

  /**
   * Manejo de situaciones de alta urgencia
   */
  private createHighUrgencyDecision(context: DecisionContext): Decision {
    const safestOption = context.alternatives
      .filter(opt => opt.riskLevel === 'low')
      .sort((a, b) => b.confidence - a.confidence)[0] || context.alternatives[0];
    
    return {
      selectedOption: safestOption,
      reasoning: `High urgency situation - selected safest option with ${(safestOption.confidence * 100).toFixed(1)}% confidence`,
      timestamp: new Date(),
      requiresHumanApproval: true,
      monitored: true
    };
  }

  /**
   * Aprendizaje de decisiones pasadas
   */
  private learnFromDecision(decision: Decision, context: DecisionContext): void {
    const patternKey = `${context.situation}_${decision.selectedOption.action}`;
    const currentConfidence = this.learningPatterns.get(patternKey) || 0;
    
    // Si la decisión fue exitosa (no requiere intervención humana), aumentar confianza
    if (!decision.requiresHumanApproval) {
      const newConfidence = Math.min(currentConfidence + 0.1, 1.0);
      this.learningPatterns.set(patternKey, newConfidence);
    }
  }

  /**
   * Obtener estadísticas de decisiones
   */
  getDecisionStats(): {
    totalDecisions: number;
    humanApprovalRate: number;
    averageConfidence: number;
    riskDistribution: Record<string, number>;
  } {
    const total = this.decisionHistory.length;
    const approvalRequired = this.decisionHistory.filter(d => d.requiresHumanApproval).length;
    const avgConfidence = this.decisionHistory.reduce((sum, d) => sum + d.selectedOption.confidence, 0) / total;
    
    const riskDistribution = this.decisionHistory.reduce((acc, d) => {
      acc[d.selectedOption.riskLevel] = (acc[d.selectedOption.riskLevel] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return {
      totalDecisions: total,
      humanApprovalRate: (approvalRequired / total) * 100,
      averageConfidence: avgConfidence,
      riskDistribution
    };
  }

  /**
   * Limpiar historial de decisiones
   */
  clearHistory(): void {
    this.decisionHistory = [];
    console.log('[DECISION ENGINE] Decision history cleared');
  }
}

// Instancia del motor de decisiones
const decisionEngine = new DecisionEngine();

export { DecisionEngine, decisionEngine, DecisionContext, DecisionOption, Decision };