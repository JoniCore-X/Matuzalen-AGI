/**
 * Cliente Cognitivo - Interfaz con el Núcleo AGI
 * 
 * Este cliente se comunica con el microservicio de razonamiento
 * que implementa la memoria vectorial y el grafo de conocimiento.
 */

interface CognitiveRequest {
  intention: string;
  context: Record<string, any>;
  urgency: 'low' | 'medium' | 'high';
  metadata?: Record<string, any>;
}

interface CognitiveResponse {
  decision: string;
  reasoning: string;
  confidence: number;
  requiresHumanApproval: boolean;
  relatedConcepts: string[];
  riskLevel: 'low' | 'medium' | 'high';
  timestamp: string;
}

interface ThoughtStep {
  type: 'doctrinal' | 'apologetic' | 'pastoral' | 'strategic' | 'experiential';
  content: string;
}

interface ThoughtPath {
  summary: string;
  doctrinal_fidelity: number;
  persuasive_effectiveness: number;
  confidence: number;
  steps: ThoughtStep[];
}

interface ToTResponse {
  intention: string;
  paths_evaluated: number;
  selected: ThoughtPath | null;
  alternatives: ThoughtPath[];
  timestamp: string;
}

class CognitiveClient {
  private apiUrl: string;
  private timeout: number;

  constructor(apiUrl: string = 'http://localhost:8000', timeout: number = 30000) {
    this.apiUrl = apiUrl;
    this.timeout = timeout;
  }

  /**
   * Envía una intención al núcleo cognitivo y recibe una decisión
   */
  async processIntention(request: CognitiveRequest): Promise<CognitiveResponse> {
    try {
      const response = await fetch(`${this.apiUrl}/cognitive/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.timeout)
      });

      if (!response.ok) {
        throw new Error(`Cognitive service error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[COGNITIVE CLIENT] Error processing intention:', error);
      
      // Fallback a modo local si el servicio no está disponible
      return this.fallbackProcessing(request);
    }
  }

  /**
   * Procesamiento de fallback cuando el servicio cognitivo no está disponible
   */
  private fallbackProcessing(request: CognitiveRequest): CognitiveResponse {
    console.warn('[COGNITIVE CLIENT] Using fallback processing');
    
    return {
      decision: `Fallback decision for: ${request.intention}`,
      reasoning: 'Cognitive service unavailable - using local processing',
      confidence: 0.5,
      requiresHumanApproval: request.urgency === 'high',
      relatedConcepts: [],
      riskLevel: request.urgency === 'high' ? 'high' : 'medium',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Invoca el motor Tree of Thoughts teológico-estratégico.
   * Devuelve el camino de razonamiento óptimo y las alternativas evaluadas.
   */
  async treeOfThoughts(intention: string, context: Record<string, any> = {}): Promise<ToTResponse | null> {
    try {
      const response = await fetch(`${this.apiUrl}/cognitive/tot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intention, context }),
        signal: AbortSignal.timeout(this.timeout)
      });
      if (!response.ok) throw new Error(`ToT service error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[COGNITIVE CLIENT] Error in Tree of Thoughts:', error);
      return null;
    }
  }

  /**
   * Verifica si el servicio cognitivo está disponible
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.apiUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000)
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Almacena conocimiento en el sistema cognitivo
   */
  async storeKnowledge(data: {
    content: string;
    type: string;
    metadata?: Record<string, any>;
  }): Promise<{ success: boolean; id?: string }> {
    try {
      const response = await fetch(`${this.apiUrl}/knowledge/store`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal: AbortSignal.timeout(this.timeout)
      });

      if (!response.ok) {
        throw new Error(`Knowledge storage error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[COGNITIVE CLIENT] Error storing knowledge:', error);
      return { success: false };
    }
  }

  /**
   * Busca conocimiento relacionado
   */
  async searchKnowledge(query: string, limit: number = 5): Promise<any[]> {
    try {
      const response = await fetch(`${this.apiUrl}/knowledge/search?query=${encodeURIComponent(query)}&limit=${limit}`, {
        method: 'GET',
        signal: AbortSignal.timeout(this.timeout)
      });

      if (!response.ok) {
        throw new Error(`Knowledge search error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[COGNITIVE CLIENT] Error searching knowledge:', error);
      return [];
    }
  }
}

// Instancia del cliente cognitivo
const cognitiveClient = new CognitiveClient();

export { CognitiveClient, cognitiveClient, CognitiveRequest, CognitiveResponse, ToTResponse, ThoughtPath, ThoughtStep };