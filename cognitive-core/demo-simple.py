"""
Demo Simplificado del Núcleo Cognitivo
Versión que no requiere Docker para pruebas iniciales
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

app = FastAPI(title="Cognitive Core Demo", version="0.1.0-demo")

# Modelos de datos
class CognitiveRequest(BaseModel):
    intention: str
    context: Dict[str, Any]
    urgency: str
    metadata: Optional[Dict[str, Any]] = None

class CognitiveResponse(BaseModel):
    decision: str
    reasoning: str
    confidence: float
    requires_human_approval: bool
    related_concepts: List[str]
    risk_level: str
    timestamp: str

class KnowledgeStore(BaseModel):
    content: str
    type: str
    metadata: Optional[Dict[str, Any]] = None

# Memoria en memoria (demo)
memory_store = []
knowledge_graph_store = []

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "demo_no_docker",
        "services": {
            "memory": len(memory_store),
            "graph": len(knowledge_graph_store),
            "reasoning": "active"
        }
    }

@app.post("/cognitive/process", response_model=CognitiveResponse)
async def process_intention(request: CognitiveRequest):
    """Procesa intención con lógica cognitiva simplificada"""
    
    # Análisis básico
    keywords = extract_keywords(request.intention)
    action_type = classify_action(request.intention)
    risk_level = assess_risk(request.intention, request.urgency)
    
    # Búsqueda en memoria (demo)
    relevant_knowledge = search_memory(request.intention)
    
    # Generación de decisión
    decision = generate_decision(
        request.intention,
        action_type,
        risk_level,
        relevant_knowledge,
        request.context
    )
    
    # Almacenar interacción
    memory_store.append({
        "intention": request.intention,
        "decision": decision,
        "timestamp": datetime.now().isoformat()
    })
    
    return CognitiveResponse(
        decision=decision["action"],
        reasoning=decision["reasoning"],
        confidence=decision["confidence"],
        requires_human_approval=decision["requires_approval"],
        related_concepts=keywords[:5],
        risk_level=risk_level,
        timestamp=datetime.now().isoformat()
    )

@app.post("/knowledge/store")
async def store_knowledge(data: KnowledgeStore):
    """Almacena conocimiento en memoria"""
    memory_store.append({
        "content": data.content,
        "type": data.type,
        "metadata": data.metadata,
        "timestamp": datetime.now().isoformat()
    })
    return {"success": True, "id": str(len(memory_store))}

@app.get("/knowledge/search")
async def search_knowledge(query: str, limit: int = 5):
    """Busca conocimiento relevante"""
    results = search_memory(query)
    return results[:limit]

# Funciones auxiliares (demo)
def extract_keywords(text: str) -> List[str]:
    stop_words = {"el", "la", "de", "en", "y", "a", "que", "por", "con"}
    words = text.lower().split()
    return [w for w in words if w not in stop_words and len(w) > 3][:10]

def classify_action(intention: str) -> str:
    intention_lower = intention.lower()
    if any(w in intention_lower for w in ["analizar", "examinar"]):
        return "analysis"
    elif any(w in intention_lower for w in ["crear", "generar"]):
        return "creation"
    elif any(w in intention_lower for w in ["ejecutar", "iniciar"]):
        return "execution"
    return "general"

def assess_risk(intention: str, urgency: str) -> str:
    high_risk = ["eliminar", "borrar", "destruir"]
    if any(w in intention.lower() for w in high_risk):
        return "high"
    if urgency == "high":
        return "medium"
    return "low"

def search_memory(query: str) -> List[Dict]:
    """Búsqueda simple en memoria"""
    query_words = set(query.lower().split())
    results = []
    
    for item in memory_store:
        content = item.get("content", "").lower()
        content_words = set(content.split())
        similarity = len(query_words & content_words) / max(len(query_words), 1)
        
        if similarity > 0.2:
            results.append({
                "content": item.get("content", ""),
                "score": similarity,
                "type": item.get("type", "unknown")
            })
    
    return sorted(results, key=lambda x: x["score"], reverse=True)[:5]

def generate_decision(intention: str, action_type: str, risk_level: str, 
                       knowledge: List[Dict], context: Dict) -> Dict:
    """Genera decisión basada en análisis"""
    
    base_action = f"Execute {action_type} for: {intention}"
    
    confidence = 0.7
    if knowledge:
        confidence += 0.2
    if risk_level == "high":
        confidence -= 0.3
    
    confidence = min(max(confidence, 0.0), 1.0)
    
    reasoning_parts = [
        f"Action type: {action_type}",
        f"Risk level: {risk_level}",
        f"Knowledge found: {len(knowledge)} items",
        f"Context keys: {len(context)}"
    ]
    
    return {
        "action": base_action,
        "reasoning": " | ".join(reasoning_parts),
        "confidence": confidence,
        "requires_approval": risk_level == "high" or confidence < 0.6
    }

if __name__ == "__main__":
    import uvicorn
    print("[COGNITIVE CORE DEMO] Starting simplified version (no Docker required)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)