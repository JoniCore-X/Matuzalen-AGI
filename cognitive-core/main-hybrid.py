"""
Núcleo Cognitivo AGI - Versión Híbrida
Funciona tanto con servicios Docker reales como en modo demo sin Docker
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Cargar configuración
load_dotenv()

# Detectar modo de operación
USE_DOCKER_SERVICES = os.getenv("USE_DOCKER_SERVICES", "false").lower() == "true"

if USE_DOCKER_SERVICES:
    print("[COGNITIVE CORE] Starting with Docker services (Qdrant + Neo4j)")
    from cognitive_memory import CognitiveMemory
    from knowledge_graph import KnowledgeGraph
    from reasoning_engine import ReasoningEngine
else:
    print("[COGNITIVE CORE] Starting in DEMO mode (no Docker required)")

# Cargar configuración teológica
THEOLOGICAL_MODE = os.getenv("THEOLOGICAL_MODE", "false").lower() == "true"

if THEOLOGICAL_MODE:
    print("[COGNITIVE CORE] Theological Reasoning Mode ENABLED")
    from theological_tot import TheologicalToT
    from knowledge_ingestion import KnowledgeIngestion
    from ollama_client import OllamaClient
else:
    print("[COGNITIVE CORE] Standard Reasoning Mode")
    TheologicalToT = None
    KnowledgeIngestion = None
    OllamaClient = None

# Cargar sistema autónomo controlado
from controlled_autonomous_system import AutonomousAPI, autonomous_system

app = FastAPI(
    title="Cognitive Core AGI - Hybrid",
    description="Núcleo de razonamiento y memoria para AGI (Modo Híbrido)",
    version="0.2.0"
)

# Inicializar componentes según modo
if USE_DOCKER_SERVICES:
    cognitive_memory = CognitiveMemory()
    knowledge_graph = KnowledgeGraph()
    reasoning_engine = ReasoningEngine(cognitive_memory, knowledge_graph)
else:
    # Memoria en memoria para demo
    cognitive_memory = None
    knowledge_graph = None
    reasoning_engine = None
    memory_store = []
    knowledge_graph_store = []

# Inicializar componentes teológicos después de que existan memoria/grafo
theological_tot = None
knowledge_ingestion = None
if THEOLOGICAL_MODE:
    ollama_client = OllamaClient()
    knowledge_ingestion = KnowledgeIngestion()
    if USE_DOCKER_SERVICES:
        theological_tot = TheologicalToT(
            ollama_client=ollama_client,
            knowledge_graph=knowledge_graph
        )
    else:
        theological_tot = TheologicalToT(ollama_client=ollama_client)

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
    mode: str

class KnowledgeStore(BaseModel):
    content: str
    type: str
    metadata: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    """Verificación de salud del servicio"""
    base_response = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "docker" if USE_DOCKER_SERVICES else "demo"
    }
    
    if USE_DOCKER_SERVICES:
        base_response["services"] = {
            "qdrant": cognitive_memory.is_healthy(),
            "neo4j": knowledge_graph.is_healthy(),
            "reasoning": reasoning_engine.is_healthy()
        }
    else:
        base_response["services"] = {
            "memory": len(memory_store),
            "graph": len(knowledge_graph_store),
            "reasoning": "active"
        }
    
    return base_response

@app.post("/cognitive/process", response_model=CognitiveResponse)
async def process_intention(request: CognitiveRequest):
    """Procesa una intención a través del núcleo cognitivo"""
    
    if USE_DOCKER_SERVICES:
        return await process_with_docker(request)
    else:
        return await process_demo(request)

async def process_with_docker(request: CognitiveRequest) -> CognitiveResponse:
    """Procesamiento con servicios Docker reales"""
    try:
        # Paso 1: Analizar la intención
        analysis = await reasoning_engine.analyze_intention(request.intention, request.context)
        
        # Paso 2: Buscar conocimiento relevante en memoria vectorial
        relevant_knowledge = await cognitive_memory.search(request.intention, limit=5)
        
        # Paso 3: Consultar grafo de conocimiento para relaciones
        graph_relations = await knowledge_graph.query_relations(request.intention, relevant_knowledge)
        
        # Paso 4: Generar decisión usando razonamiento estándar o teológico
        if THEOLOGICAL_MODE and theological_tot:
            decision = await theological_process(request, relevant_knowledge, graph_relations)
        else:
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
            timestamp=datetime.now().isoformat(),
            mode="docker_theological" if THEOLOGICAL_MODE else "docker"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cognitive processing error: {str(e)}")

async def theological_process(request: CognitiveRequest, relevant_knowledge: List[Dict], 
                             graph_relations: List[Dict]) -> Dict[str, Any]:
    """Procesamiento con motor teológico Tree of Thoughts"""
    try:
        # Enriquecer contexto con conocimiento RAG y perfil
        request.context["relevant_knowledge"] = relevant_knowledge
        request.context["profile"] = request.context.get("profile", "intelectual")
        request.context["_intention_for_effectiveness"] = request.intention

        # Generar árbol de pensamientos teológicos
        thought_paths = await theological_tot.generate_thought_tree(
            request.intention,
            request.context
        )
        
        # Seleccionar el mejor camino
        if thought_paths:
            best_path = thought_paths[0]  # Ya están ordenados por confianza
            
            decision = {
                "action": f"Theological reasoning: {best_path.nodes[-1].content}",
                "reasoning": f"ToT Path: {best_path.reasoning_summary} | Fidelity: {best_path.total_doctrinal_fidelity:.2f} | Effectiveness: {best_path.total_persuasive_effectiveness:.2f}",
                "confidence": best_path.overall_confidence,
                "requires_approval": best_path.total_doctrinal_fidelity < 0.7 or best_path.overall_confidence < 0.6,
                "related_concepts": [node.content[:50] for node in best_path.nodes[:3]],
                "risk_level": "low" if best_path.total_doctrinal_fidelity > 0.8 else "medium"
            }
        else:
            # Fallback a razonamiento estándar
            decision = await reasoning_engine.generate_decision(
                request.intention,
                request.context,
                relevant_knowledge,
                graph_relations,
                request.urgency
            )
        
        return decision
        
    except Exception as e:
        print(f"[THEOLOGICAL PROCESS] Error: {e}")
        # Fallback a razonamiento estándar
        return await reasoning_engine.generate_decision(
            request.intention,
            request.context,
            relevant_knowledge,
            graph_relations,
            request.urgency
        )

async def process_demo(request: CognitiveRequest) -> CognitiveResponse:
    """Procesamiento en modo demo (sin Docker)"""
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
        timestamp=datetime.now().isoformat(),
        mode="demo"
    )

@app.post("/knowledge/store")
async def store_knowledge(data: KnowledgeStore):
    """Almacena conocimiento en el sistema cognitivo"""
    if USE_DOCKER_SERVICES:
        return await store_knowledge_docker(data)
    else:
        return await store_knowledge_demo(data)

async def store_knowledge_docker(data: KnowledgeStore):
    """Almacenamiento con servicios Docker"""
    try:
        vector_id = await cognitive_memory.store_knowledge(data.content, data.type, data.metadata)
        entities = await reasoning_engine.extract_entities(data.content)
        graph_id = await knowledge_graph.store_entities(entities, data.metadata)
        return {"success": True, "id": f"{vector_id}_{graph_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge storage error: {str(e)}")

async def store_knowledge_demo(data: KnowledgeStore):
    """Almacenamiento en modo demo"""
    memory_store.append({
        "content": data.content,
        "type": data.type,
        "metadata": data.metadata,
        "timestamp": datetime.now().isoformat()
    })
    return {"success": True, "id": str(len(memory_store))}

class ToTRequest(BaseModel):
    intention: str
    context: Dict[str, Any] = {}

@app.post("/cognitive/tot")
async def tree_of_thoughts(request: ToTRequest):
    """Genera y evalúa múltiples caminos de razonamiento teológico-estratégico"""
    if not THEOLOGICAL_MODE or theological_tot is None:
        raise HTTPException(status_code=400, detail="THEOLOGICAL_MODE is disabled")
    paths = await theological_tot.generate_thought_tree(request.intention, request.context)
    return {
        "intention": request.intention,
        "paths_evaluated": len(paths),
        "selected": _serialize_path(paths[0]) if paths else None,
        "alternatives": [_serialize_path(p) for p in paths[1:]],
        "timestamp": datetime.now().isoformat()
    }

def _serialize_path(path) -> Dict[str, Any]:
    return {
        "summary": path.reasoning_summary,
        "doctrinal_fidelity": round(path.total_doctrinal_fidelity, 3),
        "persuasive_effectiveness": round(path.total_persuasive_effectiveness, 3),
        "confidence": round(path.overall_confidence, 3),
        "steps": [{"type": n.thought_type.value, "content": n.content} for n in path.nodes]
    }

@app.post("/knowledge/ingest")
async def ingest_knowledge_base():
    """Ingesta la base de conocimiento teológico en Qdrant + Neo4j"""
    if knowledge_ingestion is None:
        raise HTTPException(status_code=400, detail="THEOLOGICAL_MODE is disabled")
    stats = await knowledge_ingestion.run_full_ingestion()
    return {"success": stats["failed_ingestions"] == 0, "stats": stats}

@app.get("/knowledge/search")
async def search_knowledge(query: str, limit: int = 5):
    """Busca conocimiento relevante"""
    if USE_DOCKER_SERVICES:
        try:
            results = await cognitive_memory.search(query, limit)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Knowledge search error: {str(e)}")
    else:
        results = search_memory(query)
        return results[:limit]

# Funciones auxiliares demo
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

@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio"""
    print(f"[COGNITIVE CORE] Starting in {'DOCKER' if USE_DOCKER_SERVICES else 'DEMO'} mode...")
    
    if USE_DOCKER_SERVICES:
        await cognitive_memory.initialize()
        await knowledge_graph.initialize()
        await reasoning_engine.initialize()
        print("[COGNITIVE CORE] Docker services initialized successfully")
    else:
        print("[COGNITIVE CORE] Demo mode ready (no Docker required)")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza del servicio"""
    print("[COGNITIVE CORE] Shutting down cognitive services...")

    if USE_DOCKER_SERVICES:
        await cognitive_memory.close()
        await knowledge_graph.close()
        print("[COGNITIVE CORE] Docker services shutdown complete")
    else:
        print("[COGNITIVE CORE] Demo mode shutdown complete")

# Endpoints del Sistema Autónomo Controlado
class AutonomousStartRequest(BaseModel):
    controller_id: str

class AutonomousActionRequest(BaseModel):
    type: str
    data: Dict[str, Any]
    urgency: str = "medium"

class ApprovalRequest(BaseModel):
    action_id: str
    controller_id: str

@app.post("/autonomous/start")
async def start_autonomous_system(request: AutonomousStartRequest):
    """Inicia el sistema autónomo con control humano"""
    try:
        await AutonomousAPI.start(request.controller_id)
        return {"success": True, "message": "Autonomous system started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/autonomous/stop")
async def stop_autonomous_system(request: AutonomousStartRequest):
    """Detiene el sistema autónomo"""
    try:
        await AutonomousAPI.stop(request.controller_id)
        return {"success": True, "message": "Autonomous system stopped"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/autonomous/process")
async def process_autonomous_request(request: AutonomousActionRequest):
    """Procesa una solicitud autónoma con verificación de seguridad"""
    result = await AutonomousAPI.process_request(request.dict())
    return {
        "success": result.success,
        "result": result.result,
        "decision": {
            "selected_option": {
                "action": result.decision.selected_option.action if result.decision else None,
                "description": result.decision.selected_option.description if result.decision else None,
                "risk_level": result.decision.selected_option.risk_level.value if result.decision else None,
                "confidence": result.decision.selected_option.confidence if result.decision else None
            },
            "reasoning": result.decision.reasoning if result.decision else None,
            "requires_human_approval": result.decision.requires_human_approval if result.decision else None
        } if result.decision else None,
        "safety_check": {
            "allowed": result.safety_check.allowed if result.safety_check else None,
            "warnings": result.safety_check.warnings if result.safety_check else [],
            "criticals": result.safety_check.criticals if result.safety_check else []
        } if result.safety_check else None,
        "requires_human_approval": result.requires_human_approval
    }

@app.get("/autonomous/status")
async def get_autonomous_status():
    """Obtiene el estado completo del sistema autónomo"""
    return AutonomousAPI.get_status()

@app.post("/autonomous/approve")
async def approve_autonomous_action(request: ApprovalRequest):
    """Aprueba una acción pendiente"""
    try:
        approved = await AutonomousAPI.approve_action(request.action_id, request.controller_id)
        return {"success": approved, "message": "Action approved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/autonomous/reject")
async def reject_autonomous_action(request: ApprovalRequest):
    """Rechaza una acción pendiente"""
    try:
        rejected = await AutonomousAPI.reject_action(request.action_id, request.controller_id)
        return {"success": rejected, "message": "Action rejected"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)