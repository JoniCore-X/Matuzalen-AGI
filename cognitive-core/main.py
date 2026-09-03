"""
Núcleo Cognitivo AGI - Microservicio Puente
Este servicio conecta AutoPlan con las bases de datos cognitivas (Qdrant + Neo4j)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Importar módulos cognitivos
from cognitive_memory import CognitiveMemory
from knowledge_graph import KnowledgeGraph
from reasoning_engine import ReasoningEngine

load_dotenv()

app = FastAPI(
    title="Cognitive Core AGI",
    description="Núcleo de razonamiento y memoria para AGI",
    version="0.1.0"
)

# Inicializar componentes cognitivos
cognitive_memory = CognitiveMemory()
knowledge_graph = KnowledgeGraph()
reasoning_engine = ReasoningEngine(cognitive_memory, knowledge_graph)

# Modelos de datos
class CognitiveRequest(BaseModel):
    intention: str
    context: Dict[str, Any]
    urgency: str  # 'low', 'medium', 'high'
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

class KnowledgeStoreResponse(BaseModel):
    success: bool
    id: Optional[str] = None

@app.get("/health")
async def health_check():
    """Verificación de salud del servicio"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "qdrant": cognitive_memory.is_healthy(),
            "neo4j": knowledge_graph.is_healthy(),
            "reasoning": reasoning_engine.is_healthy()
        }
    }

@app.post("/cognitive/process", response_model=CognitiveResponse)
async def process_intention(request: CognitiveRequest):
    """
    Procesa una intención a través del núcleo cognitivo
    """
    try:
        # Paso 1: Analizar la intención
        analysis = await reasoning_engine.analyze_intention(request.intention, request.context)
        
        # Paso 2: Buscar conocimiento relevante en memoria vectorial
        relevant_knowledge = await cognitive_memory.search(request.intention, limit=5)
        
        # Paso 3: Consultar grafo de conocimiento para relaciones
        graph_relations = await knowledge_graph.query_relations(request.intention, relevant_knowledge)
        
        # Paso 4: Generar decisión usando razonamiento
        decision = await reasoning_engine.generate_decision(
            request.intention,
            request.context,
            relevant_knowledge,
            graph_relations,
            request.urgency
        )
        
        # Paso 5: Almacenar la interacción para aprendizaje
        await cognitive_memory.store_interaction(request.intention, decision)
        
        return CognitiveResponse(
            decision=decision["action"],
            reasoning=decision["reasoning"],
            confidence=decision["confidence"],
            requires_human_approval=decision["requires_approval"],
            related_concepts=decision["related_concepts"],
            risk_level=decision["risk_level"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cognitive processing error: {str(e)}")

@app.post("/knowledge/store", response_model=KnowledgeStoreResponse)
async def store_knowledge(data: KnowledgeStore):
    """
    Almacena conocimiento en el sistema cognitivo
    """
    try:
        # Almacenar en memoria vectorial
        vector_id = await cognitive_memory.store_knowledge(data.content, data.type, data.metadata)
        
        # Extraer entidades y relaciones para el grafo
        entities = await reasoning_engine.extract_entities(data.content)
        
        # Almacenar en grafo de conocimiento
        graph_id = await knowledge_graph.store_entities(entities, data.metadata)
        
        return KnowledgeStoreResponse(
            success=True,
            id=f"{vector_id}_{graph_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge storage error: {str(e)}")

@app.get("/knowledge/search")
async def search_knowledge(query: str, limit: int = 5):
    """
    Busca conocimiento relevante
    """
    try:
        results = await cognitive_memory.search(query, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge search error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio"""
    print("[COGNITIVE CORE] Starting cognitive services...")
    await cognitive_memory.initialize()
    await knowledge_graph.initialize()
    await reasoning_engine.initialize()
    print("[COGNITIVE CORE] All services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza del servicio"""
    print("[COGNITIVE CORE] Shutting down cognitive services...")
    await cognitive_memory.close()
    await knowledge_graph.close()
    print("[COGNITIVE CORE] Shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)