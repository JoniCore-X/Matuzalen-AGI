"""
Vistas Django REST Framework para Cognitive Core
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import os
from django.conf import settings

# Importar componentes del núcleo cognitivo
USE_DOCKER_SERVICES = settings.USE_DOCKER_SERVICES
THEOLOGICAL_MODE = settings.THEOLOGICAL_MODE

if USE_DOCKER_SERVICES:
    from cognitive_memory import CognitiveMemory
    from knowledge_graph import KnowledgeGraph
    from reasoning_engine import ReasoningEngine
else:
    CognitiveMemory = None
    KnowledgeGraph = None
    ReasoningEngine = None

if THEOLOGICAL_MODE:
    from theological_tot import TheologicalToT
    from knowledge_ingestion import KnowledgeIngestion
    from ollama_client import OllamaClient
else:
    TheologicalToT = None
    KnowledgeIngestion = None
    OllamaClient = None

# Importar sistema autónomo
from controlled_autonomous_system import AutonomousAPI

# Importar motor neuro-simbólico
from neuro_symbolic_hybrid import neuro_symbolic_engine, Paradigm

# Importar conciencia autónoma
from autonomous_consciousness import autonomous_consciousness

# Inicializar componentes
if USE_DOCKER_SERVICES:
    cognitive_memory = CognitiveMemory()
    knowledge_graph = KnowledgeGraph()
    reasoning_engine = ReasoningEngine(cognitive_memory, knowledge_graph)
else:
    cognitive_memory = None
    knowledge_graph = None
    reasoning_engine = None
    memory_store = []
    knowledge_graph_store = []

# Inicializar componentes teológicos
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


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
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

    return Response(base_response)


@api_view(['POST'])
@permission_classes([AllowAny])
def process_intention(request):
    """Procesa una intención a través del núcleo cognitivo"""
    from cognitive_api.serializers import CognitiveRequestSerializer

    serializer = CognitiveRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    if USE_DOCKER_SERVICES:
        return process_with_docker_sync(data)
    else:
        return process_demo(data)


def process_with_docker_sync(data):
    """Procesamiento con servicios Docker reales"""
    import asyncio

    async def _process_async():
        try:
            # Paso 1: Analizar la intención
            analysis = await reasoning_engine.analyze_intention(data['intention'], data['context'])

            # Paso 2: Buscar conocimiento relevante en memoria vectorial
            relevant_knowledge = await cognitive_memory.search(data['intention'], limit=5)

            # Paso 3: Consultar grafo de conocimiento para relaciones
            graph_relations = await knowledge_graph.query_relations(data['intention'], relevant_knowledge)

            # Paso 4: Generar decisión usando razonamiento estándar o teológico
            if THEOLOGICAL_MODE and theological_tot:
                decision = await theological_process_async(data, relevant_knowledge, graph_relations)
            else:
                decision = await reasoning_engine.generate_decision(
                    data['intention'],
                    data['context'],
                    relevant_knowledge,
                    graph_relations
                )

            return {
                "decision": decision['action'],
                "reasoning": decision['reasoning'],
                "confidence": decision['confidence'],
                "requires_human_approval": decision['requires_approval'],
                "related_concepts": [k.get('content', '')[:50] for k in relevant_knowledge],
                "risk_level": assess_risk(data['intention'], data['urgency']),
                "timestamp": datetime.now().isoformat(),
                "mode": "docker"
            }
        except Exception as e:
            return {
                "decision": "error",
                "reasoning": f"Error processing: {str(e)}",
                "confidence": 0.0,
                "requires_human_approval": True,
                "related_concepts": [],
                "risk_level": "high",
                "timestamp": datetime.now().isoformat(),
                "mode": "docker"
            }

    return asyncio.run(_process_async())


def process_demo(data):
    """Procesamiento en modo demo"""
    action_type = analyze_action_type(data['intention'])
    risk_level = assess_risk(data['intention'], data['urgency'])
    knowledge = search_memory(data['intention'])

    decision = generate_decision(
        data['intention'],
        action_type,
        risk_level,
        knowledge,
        data['context']
    )

    return {
        "decision": decision['action'],
        "reasoning": decision['reasoning'],
        "confidence": decision['confidence'],
        "requires_human_approval": decision['requires_approval'],
        "related_concepts": [k.get('content', '')[:50] for k in knowledge],
        "risk_level": risk_level,
        "timestamp": datetime.now().isoformat(),
        "mode": "demo"
    }


async def theological_process_async(data, knowledge, graph_relations):
    """Procesamiento teológico con Tree of Thoughts"""
    paths = await theological_tot.generate_thought_tree(data['intention'], data['context'])

    if not paths:
        return {
            'action': 'no_paths_generated',
            'reasoning': 'No valid theological paths could be generated',
            'confidence': 0.0,
            'requires_approval': True
        }

    selected_path = paths[0]
    return {
        'action': selected_path.reasoning_summary,
        'reasoning': f"Theological reasoning with {len(selected_path.nodes)} steps",
        'confidence': selected_path.overall_confidence,
        'requires_approval': selected_path.total_doctrinal_fidelity < 0.7
    }


def analyze_action_type(intention: str) -> str:
    """Analiza el tipo de acción basado en la intención"""
    action_keywords = {
        'create': 'create',
        'generate': 'create',
        'delete': 'delete',
        'remove': 'delete',
        'update': 'update',
        'modify': 'update',
        'analyze': 'analyze',
        'search': 'search',
        'find': 'search'
    }

    for keyword, action in action_keywords.items():
        if keyword in intention.lower():
            return action

    return 'general'


def assess_risk(intention: str, urgency: str) -> str:
    """Evalúa el nivel de riesgo"""
    high_risk = ["eliminar", "borrar", "destruir"]
    if any(w in intention.lower() for w in high_risk):
        return "high"
    if urgency == "high":
        return "medium"
    return "low"


def search_memory(query: str) -> list:
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
                      knowledge: list, context: dict) -> dict:
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


@api_view(['POST'])
@permission_classes([AllowAny])
def tree_of_thoughts(request):
    """Genera y evalúa múltiples caminos de razonamiento teológico-estratégico"""
    from cognitive_api.serializers import ToTRequestSerializer

    if not THEOLOGICAL_MODE or theological_tot is None:
        return Response(
            {"error": "THEOLOGICAL_MODE is disabled"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ToTRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Procesamiento asíncrono
    import asyncio

    async def _process_async():
        paths = await theological_tot.generate_thought_tree(data['intention'], data['context'])
        return {
            "intention": data['intention'],
            "paths_evaluated": len(paths),
            "selected": _serialize_path(paths[0]) if paths else None,
            "alternatives": [_serialize_path(p) for p in paths[1:]],
            "timestamp": datetime.now().isoformat()
        }

    result = asyncio.run(_process_async())
    return Response(result)


def _serialize_path(path) -> dict:
    """Serializa un camino de pensamiento"""
    return {
        "summary": path.reasoning_summary,
        "doctrinal_fidelity": round(path.total_doctrinal_fidelity, 3),
        "persuasive_effectiveness": round(path.total_persuasive_effectiveness, 3),
        "confidence": round(path.overall_confidence, 3),
        "steps": [{"type": n.thought_type.value, "content": n.content} for n in path.nodes]
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def ingest_knowledge_base(request):
    """Ingesta la base de conocimiento teológico en Qdrant + Neo4j"""
    if knowledge_ingestion is None:
        return Response(
            {"error": "THEOLOGICAL_MODE is disabled"},
            status=status.HTTP_400_BAD_REQUEST
        )

    import asyncio

    async def _process_async():
        stats = await knowledge_ingestion.run_full_ingestion()
        return {"success": stats["failed_ingestions"] == 0, "stats": stats}

    result = asyncio.run(_process_async())
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_knowledge(request):
    """Busca conocimiento relevante"""
    query = request.query_params.get('query', '')
    limit = int(request.query_params.get('limit', 5))

    if USE_DOCKER_SERVICES:
        try:
            import asyncio
            async def _search_async():
                results = await cognitive_memory.search(query, limit)
                return [
                    {
                        "content": r.get('content', ''),
                        "type": r.get('type', ''),
                        "score": r.get('score', 0),
                        "metadata": r.get('metadata', {})
                    }
                    for r in results
                ]
            results = asyncio.run(_search_async())
            return Response(results)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        results = search_memory(query)
        return Response(results)


@api_view(['POST'])
@permission_classes([AllowAny])
def store_knowledge(request):
    """Almacena conocimiento en el sistema cognitivo"""
    from cognitive_api.serializers import KnowledgeStoreSerializer

    serializer = KnowledgeStoreSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    if USE_DOCKER_SERVICES:
        try:
            import asyncio
            async def _store_async():
                vector_id = await cognitive_memory.store_knowledge(
                    content=data['content'],
                    knowledge_type=data['type'],
                    metadata=data.get('metadata', {})
                )
                return {"success": True, "id": vector_id}
            result = asyncio.run(_store_async())
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # Almacenamiento en modo demo
        memory_store.append({
            "content": data['content'],
            "type": data['type'],
            "metadata": data.get('metadata', {}),
            "timestamp": datetime.now().isoformat()
        })
        return Response({"success": True, "id": str(len(memory_store))})


# Endpoints del Sistema Autónomo Controlado
@api_view(['POST'])
@permission_classes([AllowAny])
def start_autonomous_system(request):
    """Inicia el sistema autónomo con control humano"""
    from cognitive_api.serializers import AutonomousStartRequestSerializer

    serializer = AutonomousStartRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        import asyncio
        async def _start_async():
            await AutonomousAPI.start(data['controller_id'])
            return {"success": True, "message": "Autonomous system started"}
        result = asyncio.run(_start_async())
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def stop_autonomous_system(request):
    """Detiene el sistema autónomo"""
    from cognitive_api.serializers import AutonomousStartRequestSerializer

    serializer = AutonomousStartRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        import asyncio
        async def _stop_async():
            await AutonomousAPI.stop(data['controller_id'])
            return {"success": True, "message": "Autonomous system stopped"}
        result = asyncio.run(_stop_async())
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def process_autonomous_request(request):
    """Procesa una solicitud autónoma con verificación de seguridad"""
    from cognitive_api.serializers import AutonomousActionRequestSerializer

    serializer = AutonomousActionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        import asyncio
        async def _process_async():
            result = await AutonomousAPI.process_request(data)
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
        result = asyncio.run(_process_async())
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_autonomous_status(request):
    """Obtiene el estado completo del sistema autónomo"""
    status = AutonomousAPI.get_status()
    return Response(status)


@api_view(['POST'])
@permission_classes([AllowAny])
def approve_autonomous_action(request):
    """Aprueba una acción pendiente"""
    from cognitive_api.serializers import ApprovalRequestSerializer

    serializer = ApprovalRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        import asyncio
        async def _approve_async():
            approved = await AutonomousAPI.approve_action(data['action_id'], data['controller_id'])
            return {"success": approved, "message": "Action approved"}
        result = asyncio.run(_approve_async())
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reject_autonomous_action(request):
    """Rechaza una acción pendiente"""
    from cognitive_api.serializers import ApprovalRequestSerializer

    serializer = ApprovalRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        import asyncio
        async def _reject_async():
            rejected = await AutonomousAPI.reject_action(data['action_id'], data['controller_id'])
            return {"success": rejected, "message": "Action rejected"}
        result = asyncio.run(_reject_async())
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Endpoints del Sistema Neuro-Simbólico
@api_view(['POST'])
@permission_classes([AllowAny])
def process_neuro_symbolic_task(request):
    """Procesa una tarea usando el motor neuro-simbólico"""
    from cognitive_api.serializers import NeuroSymbolicTaskSerializer

    serializer = NeuroSymbolicTaskSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        # Convertir paradigms a enum si se proporcionan
        paradigms = None
        if data.get('paradigms'):
            paradigms = [Paradigm(p) for p in data['paradigms']]

        process = neuro_symbolic_engine.process_task(
            task=data['task'],
            input_data=data['input_data'],
            paradigms=paradigms
        )

        return Response({
            "success": True,
            "task": process.task,
            "paradigms_used": [p.value for p in process.paradigms_used],
            "final_result": process.final_result,
            "confidence": process.confidence,
            "validation_passed": process.validation_passed,
            "execution_time": process.execution_time,
            "intermediate_results": {
                k: {
                    "success": v.get("success", False),
                    "result": v.get("result"),
                    "paradigm": v.get("paradigm")
                }
                for k, v in process.intermediate_results.items()
            }
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_neuro_symbolic_status(request):
    """Obtiene el estado del sistema neuro-simbólico"""
    status = neuro_symbolic_engine.get_system_status()
    return Response(status)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_domain_knowledge(request):
    """Agrega conocimiento de dominio al sistema neuro-simbólico"""
    from cognitive_api.serializers import DomainKnowledgeSerializer

    serializer = DomainKnowledgeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        neuro_symbolic_engine.add_domain_knowledge(data)
        return Response({
            "success": True,
            "message": "Domain knowledge added successfully"
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_llm_output(request):
    """Valida salida de LLM contra alucinaciones"""
    llm_output = request.data.get('output', '')
    context = request.data.get('context', '')

    try:
        validation = neuro_symbolic_engine.anti_hallucination.validate_llm_output(llm_output, context)

        return Response({
            "is_hallucination": validation.is_hallucination,
            "confidence_score": validation.confidence_score,
            "detections": [
                {
                    "type": d.type.value,
                    "severity": d.severity,
                    "location": d.location,
                    "evidence": d.evidence
                }
                for d in validation.detections
            ],
            "corrected_content": validation.corrected_content,
            "validation_method": validation.validation_method
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Endpoints de Conciencia Autónoma
@api_view(['POST'])
@permission_classes([AllowAny])
def control_consciousness(request):
    """Controla la conciencia autónoma"""
    from cognitive_api.serializers import ConsciousnessControlSerializer

    serializer = ConsciousnessControlSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    command = data['command']
    parameter = data.get('parameter', '')

    try:
        if command == 'awaken':
            autonomous_consciousness.awaken()
            return Response({
                "success": True,
                "message": "Consciousness awakened",
                "state": autonomous_consciousness.state.value
            })
        elif command == 'sleep':
            autonomous_consciousness.sleep()
            return Response({
                "success": True,
                "message": "Consciousness asleep",
                "state": autonomous_consciousness.state.value
            })
        elif command == 'focus':
            autonomous_consciousness.focus(parameter or "general monitoring")
            return Response({
                "success": True,
                "message": f"Consciousness focused on: {parameter}",
                "state": autonomous_consciousness.state.value
            })
        elif command == 'meditate':
            autonomous_consciousness.meditate()
            return Response({
                "success": True,
                "message": "Consciousness meditating",
                "state": autonomous_consciousness.state.value
            })
        else:
            return Response({"error": "Unknown command"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_consciousness_state(request):
    """Obtiene el estado de la conciencia autónoma"""
    state = autonomous_consciousness.get_consciousness_state()
    return Response(state)


@api_view(['POST'])
@permission_classes([AllowAny])
def set_perception_interval(request):
    """Ajusta el intervalo de percepción"""
    interval = request.data.get('interval', 5.0)

    try:
        interval = float(interval)
        autonomous_consciousness.set_perception_interval(interval)
        return Response({
            "success": True,
            "message": f"Perception interval set to {interval}s",
            "interval": interval
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Página raíz de la API"""
    return Response({
        "name": "AutoPlan AGI - Neuro-Symbolic Cognitive Core",
        "version": "1.0.0",
        "description": "Sistema cognitivo neuro-simbólico con conciencia autónoma",
        "endpoints": {
            "health": "/api/health/",
            "consciousness": {
                "control": "/api/consciousness/control",
                "state": "/api/consciousness/state",
                "interval": "/api/consciousness/interval"
            },
            "neuro_symbolic": {
                "process": "/api/neuro-symbolic/process",
                "status": "/api/neuro-symbolic/status",
                "knowledge": "/api/neuro-symbolic/knowledge",
                "validate": "/api/neuro-symbolic/validate"
            },
            "autonomous": {
                "start": "/api/autonomous/start",
                "stop": "/api/autonomous/stop",
                "process": "/api/autonomous/process",
                "status": "/api/autonomous/status",
                "approve": "/api/autonomous/approve",
                "reject": "/api/autonomous/reject"
            },
            "cognitive": {
                "process": "/api/cognitive/process",
                "tot": "/api/cognitive/tot",
                "knowledge_ingest": "/api/knowledge/ingest",
                "knowledge_search": "/api/knowledge/search",
                "knowledge_store": "/api/knowledge/store"
            }
        },
        "consciousness_state": autonomous_consciousness.get_consciousness_state(),
        "documentation": "Ver /api/health/ para verificar estado del sistema"
    })
