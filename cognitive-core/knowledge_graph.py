"""
Grafo de Conocimiento - Sistema de Memoria Relacional
Implementa almacenamiento y consulta de relaciones usando Neo4j
"""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

class KnowledgeGraph:
    def __init__(self):
        self.driver = None
        self.uri = "bolt://localhost:7687"
        self.username = "neo4j"
        self.password = "ultron_cognitive_2026"
        self.initialized = False

    async def initialize(self):
        """Inicializa la conexión con Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            
            # Verificar conexión
            self.driver.verify_connectivity()
            
            # Crear índices si no existen
            self._create_indexes()
            
            self.initialized = True
            print("[KNOWLEDGE GRAPH] Initialized successfully")
            
        except Exception as e:
            print(f"[KNOWLEDGE GRAPH] Initialization error: {e}")
            raise

    def _create_indexes(self):
        """Crea índices para optimizar consultas"""
        with self.driver.session() as session:
            # Índice para entidades
            session.run("CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)")
            
            # Índice para conceptos
            session.run("CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)")
            
            # Índice para relaciones
            session.run("CREATE INDEX relation_type IF NOT EXISTS FOR ()-[r:RELATED_TO]->() ON (r.type)")

    async def store_entities(self, entities: List[Dict[str, Any]], metadata: Optional[Dict] = None):
        """Almacena entidades y sus relaciones en el grafo"""
        try:
            # Neo4j solo acepta propiedades primitivas: aplanar metadata con prefijo
            flat_meta = {f"meta_{k}": v for k, v in (metadata or {}).items()
                         if isinstance(v, (str, int, float, bool)) or
                         (isinstance(v, list) and all(isinstance(i, (str, int, float, bool)) for i in v))}
            with self.driver.session() as session:
                for entity in entities:
                    # Crear nodo de entidad
                    session.run(
                        """
                        MERGE (e:Entity {name: $name})
                        SET e.type = $type, 
                            e.confidence = $confidence,
                            e.timestamp = $timestamp,
                            e += $metadata
                        """,
                        name=entity.get("name", ""),
                        type=entity.get("type", "unknown"),
                        confidence=entity.get("confidence", 0.0),
                        timestamp=datetime.now().isoformat(),
                        metadata=flat_meta
                    )
                
                # Crear relaciones entre entidades
                if len(entities) > 1:
                    for i in range(len(entities) - 1):
                        session.run(
                            """
                            MATCH (a:Entity {name: $name1})
                            MATCH (b:Entity {name: $name2})
                            MERGE (a)-[r:RELATED_TO]->(b)
                            SET r.type = $relation_type,
                                r.strength = $strength,
                                r.timestamp = $timestamp
                            """,
                            name1=entities[i].get("name", ""),
                            name2=entities[i+1].get("name", ""),
                            relation_type="semantic_relation",
                            strength=0.8,
                            timestamp=datetime.now().isoformat()
                        )
            
            return "entities_stored"
            
        except Exception as e:
            print(f"[KNOWLEDGE GRAPH] Error storing entities: {e}")
            raise

    async def query_relations(self, query: str, relevant_knowledge: List[Dict]) -> List[Dict[str, Any]]:
        """Consulta relaciones en el grafo basadas en el conocimiento relevante"""
        try:
            with self.driver.session() as session:
                # Extraer entidades del conocimiento relevante
                entities = self._extract_entities_from_knowledge(relevant_knowledge)
                
                if not entities:
                    return []
                
                # Consultar relaciones para estas entidades
                relations = []
                for entity_name in entities[:5]:  # Limitar a 5 entidades para rendimiento
                    result = session.run(
                        """
                        MATCH (e:Entity {name: $name})-[r:RELATED_TO]->(related)
                        RETURN e.name as entity, 
                               related.name as related_entity, 
                               r.type as relation_type,
                               r.strength as strength
                        LIMIT 10
                        """,
                        name=entity_name
                    )
                    
                    for record in result:
                        relations.append({
                            "entity": record["entity"],
                            "related_entity": record["related_entity"],
                            "relation_type": record["relation_type"],
                            "strength": record["strength"]
                        })
                
                return relations
                
        except Exception as e:
            print(f"[KNOWLEDGE GRAPH] Error querying relations: {e}")
            return []

    def _extract_entities_from_knowledge(self, knowledge_list: List[Dict]) -> List[str]:
        """Extrae nombres de entidades del conocimiento relevante"""
        entities = []
        for knowledge in knowledge_list:
            content = knowledge.get("content", "")
            # Extracción simple - en producción usar NLP
            words = content.split()
            # Palabras que parecen entidades (capitalizadas, >3 caracteres)
            potential_entities = [word for word in words if len(word) > 3 and word[0].isupper()]
            entities.extend(potential_entities[:3])  # Top 3 por conocimiento
        
        return list(set(entities))  # Eliminar duplicados

    async def create_concept_node(self, concept: str, attributes: Dict[str, Any]):
        """Crea un nodo de concepto en el grafo"""
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (c:Concept {name: $name})
                    SET c += $attributes,
                        c.timestamp = $timestamp
                    """,
                    name=concept,
                    attributes={k: v for k, v in attributes.items()
                                if isinstance(v, (str, int, float, bool, list))},
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"[KNOWLEDGE GRAPH] Error creating concept: {e}")

    async def relate_fragments(self, fragment1: str, fragment2: str, relation_type: str = "SE_RELACIONA_CON", strength: float = 0.9):
        """Crea una relación tipada (:SE_RELACIONA_CON) entre fragmentos por similitud vectorial."""
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (a {name: $name1}) WHERE a:Concept OR a:Entity
                    MATCH (b {name: $name2}) WHERE b:Concept OR b:Entity
                    MERGE (a)-[r:SE_RELACIONA_CON]->(b)
                    SET r.strength = $strength,
                        r.similarity = $strength,
                        r.timestamp = $timestamp
                    """,
                    name1=fragment1,
                    name2=fragment2,
                    strength=float(strength),
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"[KNOWLEDGE GRAPH] Error relating fragments: {e}")

    async def verify_entity_in_graph(self, entity: str) -> Dict[str, Any]:
        """Valida si una entidad extraída del LLM existe en el grafo y su soporte doctrinal."""
        result = {
            "entity": entity,
            "matched_nodes": [],
            "refuted_objections": [],
            "supported_doctrines": [],
            "suggested_strategies": [],
            "orthodox_score": 0.0
        }
        if not self.initialized or not self.driver:
            return result
        try:
            with self.driver.session() as session:
                # 1. Nodos cuyo nombre contenga la entidad o viceversa (normalizando guiones bajos)
                nodes = session.run(
                    """
                    MATCH (n)
                    WHERE n.name IS NOT NULL
                      AND (toLower(replace(n.name, '_', ' ')) CONTAINS toLower(replace($entity, '_', ' '))
                           OR toLower(replace($entity, '_', ' ')) CONTAINS toLower(replace(n.name, '_', ' ')))
                    RETURN labels(n) AS labels, n.name AS name
                    LIMIT 10
                    """,
                    entity=entity
                )
                for record in nodes:
                    labels = record["labels"]
                    name = record["name"]
                    result["matched_nodes"].append({"labels": labels, "name": name})

                # 2. Doctrina que REFUTA una Objeción identificada
                refutations = session.run(
                    """
                    MATCH (d:Doctrina)-[:REFUTA]->(o:Objecion)
                    WHERE toLower(replace(o.name, '_', ' ')) CONTAINS toLower(replace($entity, '_', ' '))
                       OR toLower(replace($entity, '_', ' ')) CONTAINS toLower(replace(o.name, '_', ' '))
                    RETURN d.name AS doctrine, o.name AS objection
                    LIMIT 10
                    """,
                    entity=entity
                )
                for record in refutations:
                    result["refuted_objections"].append({
                        "doctrine": record["doctrine"],
                        "objection": record["objection"]
                    })

                # 3. Doctrinas soportadas por la entidad (si la entidad es doctrina)
                supported = session.run(
                    """
                    MATCH (d1:Doctrina)-[:SOPORTA]->(d2:Doctrina)
                    WHERE toLower(replace(d1.name, '_', ' ')) CONTAINS toLower(replace($entity, '_', ' '))
                       OR toLower(replace($entity, '_', ' ')) CONTAINS toLower(replace(d1.name, '_', ' '))
                    RETURN d1.name AS source, d2.name AS target
                    LIMIT 10
                    """,
                    entity=entity
                )
                for record in supported:
                    result["supported_doctrines"].append({
                        "source": record["source"],
                        "target": record["target"]
                    })

                # 4. Estrategia sugerida para un estado o perfil
                strategies = session.run(
                    """
                    MATCH (s)-[:REQUIERE_ESTRATEGIA]->(e:Estrategia_Conversion)
                    WHERE (s:Estado_Espiritual OR s:Perfil)
                      AND (toLower(replace(s.name, '_', ' ')) CONTAINS toLower(replace($entity, '_', ' '))
                           OR toLower(replace($entity, '_', ' ')) CONTAINS toLower(replace(s.name, '_', ' ')))
                    RETURN s.name AS state, e.name AS strategy
                    LIMIT 10
                    """,
                    entity=entity
                )
                for record in strategies:
                    result["suggested_strategies"].append({
                        "state": record["state"],
                        "strategy": record["strategy"]
                    })

                # Puntuación ortodoxa heurística
                score = 0.0
                if result["matched_nodes"]:
                    for node in result["matched_nodes"]:
                        if "Doctrina" in node["labels"] or "Argumento" in node["labels"]:
                            score += 0.35
                        elif "Estrategia_Conversion" in node["labels"]:
                            score += 0.25
                        elif "Perfil" in node["labels"] or "Estado_Espiritual" in node["labels"]:
                            score += 0.20
                        elif "Objecion" in node["labels"]:
                            score -= 0.10  # es una objeción a menos que esté refutada
                if result["refuted_objections"]:
                    score += 0.25 * len(result["refuted_objections"])
                if result["supported_doctrines"]:
                    score += 0.20 * len(result["supported_doctrines"])
                if result["suggested_strategies"]:
                    score += 0.15 * len(result["suggested_strategies"])
                result["orthodox_score"] = min(max(score, 0.0), 1.0)
        except Exception as e:
            print(f"[KNOWLEDGE GRAPH] Error verifying entity '{entity}': {type(e).__name__}: {e}")
        return result

    async def relate_concepts(self, concept1: str, concept2: str, relation_type: str, strength: float = 0.5):
        """Crea una relación entre dos conceptos"""
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (c1 {name: $name1}) WHERE c1:Concept OR c1:Entity
                    MATCH (c2 {name: $name2}) WHERE c2:Concept OR c2:Entity
                    MERGE (c1)-[r:RELATED_TO]->(c2)
                    SET r.type = $relation_type,
                        r.strength = $strength,
                        r.timestamp = $timestamp
                    """,
                    name1=concept1,
                    name2=concept2,
                    relation_type=relation_type,
                    strength=strength,
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"[KNOWLEDGE GRAPH] Error relating concepts: {e}")

    def is_healthy(self) -> bool:
        """Verifica si el servicio está saludable"""
        try:
            if not self.initialized or not self.driver:
                return False
            self.driver.verify_connectivity()
            return True
        except:
            return False

    async def close(self):
        """Cierra la conexión"""
        if self.driver:
            self.driver.close()
        print("[KNOWLEDGE GRAPH] Connection closed")