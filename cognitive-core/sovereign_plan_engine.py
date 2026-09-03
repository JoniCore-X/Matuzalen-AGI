"""
Sovereign Plan Engine - Persistencia de la Voluntad

Combina:
- Neo4j: Grafo de ejecucion con Event Sourcing
- Qdrant: Sombra semantica vectorial del plan
- Ollama: Embeddings locales

Un plan no es un archivo JSON. Es una estructura cognitiva viva.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import httpx
import asyncio


class SovereignPlanEngine:
    """Motor de persistencia de planes como estructuras cognitivas vivas."""

    def __init__(self):
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "ultron_cognitive_2026")
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.vector_size = int(os.getenv("EMBEDDING_DIMENSION", "768"))
        self.collection_name = "sovereign_plans"

        self.neo4j_driver = None
        self.qdrant_client = None

    def connect(self):
        """Conecta con Neo4j y Qdrant."""
        try:
            self.neo4j_driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            print(f"[SOVEREIGN PLAN] Neo4j connected: {self.neo4j_uri}")
        except Exception as e:
            print(f"[SOVEREIGN PLAN] Neo4j connection failed: {e}")
            self.neo4j_driver = None

        try:
            self.qdrant_client = QdrantClient(
                host=self.qdrant_host,
                port=self.qdrant_port,
                timeout=60
            )
            self._ensure_qdrant_collection()
            print(f"[SOVEREIGN PLAN] Qdrant connected: {self.qdrant_host}:{self.qdrant_port}")
        except Exception as e:
            print(f"[SOVEREIGN PLAN] Qdrant connection failed: {e}")
            self.qdrant_client = None

    def _ensure_qdrant_collection(self):
        """Asegura que exista la coleccion de planes en Qdrant."""
        try:
            collections = self.qdrant_client.get_collections().collections
            names = [c.name for c in collections]
            if self.collection_name not in names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"[SOVEREIGN PLAN] Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"[SOVEREIGN PLAN] Qdrant collection error: {e}")

    async def _get_embedding(self, text: str) -> List[float]:
        """Obtiene embedding local via Ollama."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.ollama_host}/api/embed",
                json={"model": self.embedding_model, "input": [text]}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embeddings", [[]])[0]

    def create_plan(self, user_id: str, nombre: str, proposito: str) -> Optional[str]:
        """Crea un plan como grafo en Neo4j."""
        if not self.neo4j_driver:
            print("[SOVEREIGN PLAN] Neo4j not connected")
            return None

        plan_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (u:Usuario {id: $user_id})
                ON CREATE SET u.identity_node = 'Usuario:Arquitecto',
                              u.spiritual_profile = 'Estratega_Dominante',
                              u.clearance_level = 'Omega',
                              u.created_at = $timestamp
                CREATE (p:Plan {
                    id: $plan_id,
                    user_id: $user_id,
                    nombre: $nombre,
                    proposito: $proposito,
                    estado: 'activo',
                    activo: true,
                    created_at: $timestamp,
                    updated_at: $timestamp
                })
                CREATE (u)-[:POSEE {desde: $timestamp}]->(p)
            """, user_id=user_id, plan_id=plan_id, nombre=nombre,
                proposito=proposito, timestamp=timestamp)

            # Event sourcing
            session.run("""
                MATCH (p:Plan {id: $plan_id})
                CREATE (e:Evento {
                    id: $event_id,
                    plan_id: $plan_id,
                    tipo: 'PLAN_CREADO',
                    actor: $user_id,
                    timestamp: $timestamp,
                    payload: $payload
                })
                CREATE (p)-[:TIENE_EVENTO]->(e)
            """, plan_id=plan_id, event_id=str(uuid.uuid4()), user_id=user_id,
                timestamp=timestamp, payload=json.dumps({
                    "plan_id": plan_id,
                    "nombre": nombre,
                    "proposito": proposito
                }))

        print(f"[SOVEREIGN PLAN] Created plan {plan_id}")
        return plan_id

    def add_objective(self, plan_id: str, descripcion: str, criterio_exito: str, prioridad: float = 1.0) -> Optional[str]:
        """Agrega un objetivo al plan."""
        if not self.neo4j_driver:
            return None

        objetivo_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (p:Plan {id: $plan_id})
                CREATE (o:Objetivo {
                    id: $objetivo_id,
                    plan_id: $plan_id,
                    descripcion: $descripcion,
                    criterio_exito: $criterio_exito,
                    prioridad: $prioridad
                })
                CREATE (p)-[:TIENE_OBJETIVO {peso: $prioridad}]->(o)
                RETURN o.id AS objetivo_id
            """, plan_id=plan_id, objetivo_id=objetivo_id, descripcion=descripcion,
                criterio_exito=criterio_exito, prioridad=prioridad)
            if not result.single():
                return None

            session.run("""
                MATCH (p:Plan {id: $plan_id})
                CREATE (e:Evento {
                    id: $event_id,
                    plan_id: $plan_id,
                    tipo: 'OBJETIVO_AGREGADO',
                    actor: 'AGI',
                    timestamp: $timestamp,
                    payload: $payload
                })
                CREATE (p)-[:TIENE_EVENTO]->(e)
            """, plan_id=plan_id, event_id=str(uuid.uuid4()), timestamp=timestamp,
                payload=json.dumps({"objetivo_id": objetivo_id, "descripcion": descripcion}))

        return objetivo_id

    def add_phase(self, plan_id: str, nombre: str, orden: int, estado: str = "pendiente") -> Optional[str]:
        """Agrega una fase al plan."""
        if not self.neo4j_driver:
            return None

        fase_id = str(uuid.uuid4())

        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (p:Plan {id: $plan_id})
                CREATE (f:Fase {
                    id: $fase_id,
                    plan_id: $plan_id,
                    nombre: $nombre,
                    orden: $orden,
                    estado: $estado
                })
                CREATE (p)-[:CONTIENE_FASE {orden: $orden}]->(f)
                RETURN f.id AS fase_id
            """, plan_id=plan_id, fase_id=fase_id, nombre=nombre, orden=orden, estado=estado)
            if not result.single():
                return None

        return fase_id

    def add_action(self, fase_id: str, descripcion: str, prioridad: float = 0.5) -> Optional[str]:
        """Agrega una accion a una fase."""
        if not self.neo4j_driver:
            return None

        accion_id = str(uuid.uuid4())

        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (f:Fase {id: $fase_id})
                CREATE (a:Accion {
                    id: $accion_id,
                    fase_id: $fase_id,
                    descripcion: $descripcion,
                    estado: 'pendiente',
                    prioridad: $prioridad
                })
                CREATE (f)-[:INCLUYE_ACCION]->(a)
                RETURN a.id AS accion_id
            """, fase_id=fase_id, accion_id=accion_id, descripcion=descripcion, prioridad=prioridad)
            if not result.single():
                return None

        return accion_id

    def add_risk(self, action_id: str, descripcion: str, probabilidad: float, impacto: float) -> Optional[str]:
        """Agrega un riesgo a una accion."""
        if not self.neo4j_driver:
            return None

        riesgo_id = str(uuid.uuid4())

        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (p:Plan)-[:CONTIENE_FASE]->(f:Fase)-[:INCLUYE_ACCION]->(a:Accion {id: $action_id})
                CREATE (r:Riesgo {
                    id: $riesgo_id,
                    plan_id: p.id,
                    descripcion: $descripcion,
                    probabilidad: $probabilidad,
                    impacto: $impacto
                })
                CREATE (a)-[:BLOQUEA {severidad: $severidad}]->(r)
                RETURN r.id AS riesgo_id
            """, action_id=action_id, riesgo_id=riesgo_id,
                descripcion=descripcion, probabilidad=probabilidad, impacto=impacto,
                severidad=probabilidad * impacto)
            record = result.single()
            if not record:
                return None

        return riesgo_id

    def update_action_status(self, action_id: str, new_status: str, reason: str = "", actor: str = "AGI") -> bool:
        """Actualiza el estado de una accion y registra un evento."""
        if not self.neo4j_driver:
            return False

        timestamp = datetime.now().isoformat()

        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (a:Accion {id: $action_id})
                RETURN a.estado AS old_status, a.fase_id AS fase_id
            """, action_id=action_id)
            record = result.single()
            if not record:
                return False

            old_status = record["old_status"]
            fase_id = record["fase_id"]

            plan_result = session.run("""
                MATCH (f:Fase {id: $fase_id})<-[:CONTIENE_FASE]-(p:Plan)
                RETURN p.id AS plan_id
            """, fase_id=fase_id)
            plan_record = plan_result.single()
            plan_id = plan_record["plan_id"] if plan_record else None

            session.run("""
                MATCH (a:Accion {id: $action_id})
                SET a.estado = $new_status, a.updated_at = $timestamp
            """, action_id=action_id, new_status=new_status, timestamp=timestamp)

            session.run("""
                MATCH (p:Plan {id: $plan_id})
                CREATE (e:Evento {
                    id: $event_id,
                    plan_id: $plan_id,
                    tipo: $tipo,
                    actor: $actor,
                    timestamp: $timestamp,
                    payload: $payload
                })
                CREATE (p)-[:TIENE_EVENTO]->(e)
            """, plan_id=plan_id, event_id=str(uuid.uuid4()),
                tipo="ACCION_MODIFICADA" if new_status != "refutado" else "ACCION_REFUTADA_POR_CORTEX",
                actor=actor, timestamp=timestamp,
                payload=json.dumps({
                    "accion_id": action_id,
                    "estado_anterior": old_status,
                    "estado_nuevo": new_status,
                    "razon": reason
                }))

        return True

    def refute_action(self, action_id: str, reason: str, new_action_description: Optional[str] = None) -> Optional[str]:
        """Refuta una accion y opcionalmente crea una nueva ruta."""
        if not self.neo4j_driver:
            return None

        self.update_action_status(action_id, "refutado", reason, actor="AGI")

        new_action_id = None
        if new_action_description:
            # Crear nueva accion en la misma fase
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (a:Accion {id: $action_id})
                    RETURN a.fase_id AS fase_id
                """, action_id=action_id)
                record = result.single()
                if record:
                    new_action_id = self.add_action(
                        record["fase_id"],
                        new_action_description,
                        prioridad=0.9
                    )

        return new_action_id

    async def store_semantic_shadow(self, plan_id: str, user_id: str, content: str, content_type: str = "plan_summary") -> bool:
        """Guarda la sombra semantica del plan en Qdrant."""
        if not self.qdrant_client:
            return False

        try:
            embedding = await self._get_embedding(content)
            point_id = str(uuid.uuid4())

            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "plan_id": plan_id,
                        "user_id": user_id,
                        "content": content,
                        "content_type": content_type,
                        "timestamp": datetime.now().isoformat()
                    }
                )]
            )
            return True
        except Exception as e:
            print(f"[SOVEREIGN PLAN] Qdrant semantic shadow error: {e}")
            return False

    async def search_semantic_shadow(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca en la sombra semantica del plan."""
        if not self.qdrant_client:
            return []

        try:
            from qdrant_client.models import SearchRequest, Filter, FieldCondition, MatchValue

            embedding = await self._get_embedding(query)
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                query_filter=Filter(
                    must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
                ),
                limit=limit,
                with_payload=True
            )

            return [{
                "id": r.id,
                "score": r.score,
                "content": r.payload.get("content", ""),
                "content_type": r.payload.get("content_type", ""),
                "plan_id": r.payload.get("plan_id", ""),
                "timestamp": r.payload.get("timestamp", "")
            } for r in results]
        except Exception as e:
            print(f"[SOVEREIGN PLAN] Semantic search error: {e}")
            return []

    def get_active_plan_context(self, user_id: str) -> Dict[str, Any]:
        """Obtiene el contexto cognitivo del plan activo para inyectar en el system prompt."""
        if not self.neo4j_driver:
            return {}

        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (u:Usuario {id: $user_id})-[:POSEE]->(p:Plan {activo: true})
                OPTIONAL MATCH (p)-[:CONTIENE_FASE]->(f:Fase)
                OPTIONAL MATCH (f)-[:INCLUYE_ACCION]->(a:Accion)
                OPTIONAL MATCH (a)-[:BLOQUEA]->(r:Riesgo)
                OPTIONAL MATCH (a)-[:REQUIERE]->(rec:Recurso)
                RETURN p.id AS plan_id, p.nombre AS plan_nombre, p.proposito AS proposito,
                       collect(DISTINCT {
                         id: f.id, nombre: f.nombre, orden: f.orden, estado: f.estado
                       }) AS fases,
                       collect(DISTINCT {
                         id: a.id, descripcion: a.descripcion, fase_id: a.fase_id,
                         estado: a.estado, prioridad: a.prioridad
                       }) AS acciones,
                       collect(DISTINCT {
                         id: r.id, descripcion: r.descripcion, probabilidad: r.probabilidad,
                         impacto: r.impacto, accion_id: a.id
                       }) AS riesgos,
                       collect(DISTINCT {
                         id: rec.id, nombre: rec.nombre, tipo: rec.tipo
                       }) AS recursos
            """, user_id=user_id)

            record = result.single()
            if not record:
                return {}

            # Detectar cuellos de botella criticos
            riesgos = record["riesgos"]
            critical_risks = [
                r for r in riesgos
                if float(r.get("probabilidad") or 0) * float(r.get("impacto") or 0) > 0.5
            ]

            # Proximos pasos logicos
            pending_actions = [
                a for a in record["acciones"]
                if a.get("estado") == "pendiente"
            ]
            pending_actions.sort(key=lambda x: x.get("prioridad", 0), reverse=True)
            next_steps = pending_actions[:3]

            return {
                "plan_id": record["plan_id"],
                "plan_nombre": record["plan_nombre"],
                "proposito": record["proposito"],
                "fases": record["fases"],
                "acciones": record["acciones"],
                "riesgos": record["riesgos"],
                "recursos": record["recursos"],
                "critical_risks": critical_risks,
                "next_steps": next_steps
            }

    def get_plan_event_history(self, plan_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtiene la historia de eventos de un plan (event sourcing)."""
        if not self.neo4j_driver:
            return []

        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (p:Plan {id: $plan_id})-[:TIENE_EVENTO]->(e:Evento)
                RETURN e.tipo AS tipo, e.actor AS actor, e.timestamp AS timestamp, e.payload AS payload
                ORDER BY e.timestamp DESC
                LIMIT $limit
            """, plan_id=plan_id, limit=limit)

            return [{
                "tipo": r["tipo"],
                "actor": r["actor"],
                "timestamp": r["timestamp"],
                "payload": r["payload"]
            } for r in result]

    def close(self):
        if self.neo4j_driver:
            self.neo4j_driver.close()


# Instancia global del motor de planes soberanos
plan_engine = SovereignPlanEngine()
