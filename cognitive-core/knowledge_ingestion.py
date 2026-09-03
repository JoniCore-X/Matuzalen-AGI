"""
Sistema de Ingestión de Conocimiento Teológico
Prepara y carga los textos base en Qdrant y Neo4j cuando los servicios estén disponibles
"""

import json
import asyncio
from typing import List, Dict, Any
from pathlib import Path
import os

# Intentar importar servicios reales, usar modo demo si no están disponibles
try:
    from cognitive_memory import CognitiveMemory
    from knowledge_graph import KnowledgeGraph
    from theological_tot import TheologicalToT
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    print("[KNOWLEDGE INGESTION] Services not available, using demo mode")

class KnowledgeIngestion:
    """Sistema de ingestión de conocimiento teológico"""
    
    def __init__(self):
        self.knowledge_base_path = Path(__file__).parent / "knowledge_base" / "teological_texts.json"
        self.ingestion_stats = {
            "total_fragments": 0,
            "successful_ingestions": 0,
            "failed_ingestions": 0,
            "vector_db_entries": 0,
            "graph_db_entries": 0,
            "doctrinal_relationships": 0,
            "synaptic_relationships": 0
        }
        
        if SERVICES_AVAILABLE:
            self.cognitive_memory = CognitiveMemory()
            self.knowledge_graph = KnowledgeGraph()
            self.tot_engine = TheologicalToT()
    
    async def initialize_services(self):
        """Inicializa los servicios cognitivos"""
        if SERVICES_AVAILABLE:
            await self.cognitive_memory.initialize()
            await self.knowledge_graph.initialize()
            print("[KNOWLEDGE INGESTION] Services initialized successfully")
        else:
            print("[KNOWLEDGE INGESTION] Running in demo mode (no real services)")
    
    async def load_knowledge_base(self) -> Dict[str, Any]:
        """Carga el archivo de base de conocimiento"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.ingestion_stats["total_fragments"] = len(data["knowledge_base"]["fragments"])
            print(f"[KNOWLEDGE INGESTION] Loaded {self.ingestion_stats['total_fragments']} fragments")
            return data
            
        except Exception as e:
            print(f"[KNOWLEDGE INGESTION] Error loading knowledge base: {e}")
            return {"knowledge_base": {"fragments": []}}
    
    async def ingest_to_vector_db(self, fragments: List[Dict[str, Any]]) -> int:
        """Ingresa fragmentos en la base de datos vectorial (Qdrant)"""
        vector_count = 0
        
        for fragment in fragments:
            try:
                # Preparar contenido para embedding
                content = self._prepare_vector_content(fragment)
                
                if SERVICES_AVAILABLE:
                    # Ingestión real en Qdrant
                    vector_id = await self.cognitive_memory.store_knowledge(
                        content=content,
                        knowledge_type=fragment["type"],
                        metadata={
                            "id": fragment["id"],
                            "category": fragment["category"],
                            "doctrinal_weight": fragment.get("doctrinal_weight", 0.0),
                            "strategic_importance": fragment.get("strategic_importance", 0.0),
                            "keywords": fragment.get("keywords", [])
                        }
                    )
                    vector_count += 1
                    print(f"[VECTOR DB] Ingested fragment {fragment['id']}: {vector_id}")
                else:
                    # Simulación en modo demo
                    vector_count += 1
                    print(f"[VECTOR DB DEMO] Would ingest fragment {fragment['id']}")
                    
            except Exception as e:
                print(f"[VECTOR DB] Error ingesting fragment {fragment['id']}: {e}")
                self.ingestion_stats["failed_ingestions"] += 1
        
        self.ingestion_stats["vector_db_entries"] = vector_count
        return vector_count
    
    async def ingest_to_graph_db(self, fragments: List[Dict[str, Any]]) -> int:
        """Ingresa fragmentos en el grafo de conocimiento (Neo4j)"""
        graph_count = 0
        
        for fragment in fragments:
            try:
                # Extraer entidades y relaciones del fragmento
                entities = self._extract_entities(fragment)
                
                if SERVICES_AVAILABLE:
                    # Ingestión real en Neo4j
                    graph_id = await self.knowledge_graph.store_entities(
                        entities,
                        metadata={
                            "fragment_id": fragment["id"],
                            "type": fragment["type"],
                            "category": fragment["category"]
                        }
                    )
                    graph_count += 1
                    print(f"[GRAPH DB] Ingested fragment {fragment['id']}: {graph_id}")
                else:
                    # Simulación en modo demo
                    graph_count += 1
                    print(f"[GRAPH DB DEMO] Would ingest fragment {fragment['id']}")
                    
            except Exception as e:
                print(f"[GRAPH DB] Error ingesting fragment {fragment['id']}: {e}")
                self.ingestion_stats["failed_ingestions"] += 1
        
        self.ingestion_stats["graph_db_entries"] = graph_count
        return graph_count
    
    async def create_synaptic_relationships(self, fragments: List[Dict[str, Any]]) -> int:
        """Crea relaciones (:SE_RELACIONA_CON) entre fragmentos con similitud vectorial > 0.85."""
        if not SERVICES_AVAILABLE:
            print("[GRAPH DB DEMO] Would create synaptic vector-graph relationships")
            return 0

        relationship_count = 0
        threshold = 0.85
        seen = set()

        for fragment in fragments:
            try:
                content = self._prepare_vector_content(fragment)
                related = await self.cognitive_memory.find_semantic_relationships(
                    content=content,
                    own_id=fragment["id"],
                    threshold=threshold,
                    limit=5
                )

                for rel in related:
                    other_id = rel.get("id")
                    if not other_id:
                        continue
                    # Evitar duplicados sin importar dirección
                    pair = tuple(sorted([fragment["id"], other_id]))
                    if pair in seen:
                        continue
                    seen.add(pair)

                    await self.knowledge_graph.relate_fragments(
                        fragment1=fragment["id"],
                        fragment2=other_id,
                        relation_type="SE_RELACIONA_CON",
                        strength=rel.get("score", 0.85)
                    )
                    relationship_count += 1
                    print(f"[SYNAPSE] {fragment['id']} --[:SE_RELACIONA_CON {rel.get('score',0):.3f}]--> {other_id}")
            except Exception as e:
                print(f"[SYNAPSE] Error for fragment {fragment['id']}: {type(e).__name__}: {e}")

        return relationship_count

    async def create_doctrinal_relationships(self, fragments: List[Dict[str, Any]]) -> int:
        """Crea relaciones doctrinales específicas en el grafo"""
        relationship_count = 0
        
        if not SERVICES_AVAILABLE:
            print("[GRAPH DB DEMO] Would create doctrinal relationships")
            return len(fragments)
        
        # Crear relaciones entre doctrinas relacionadas
        doctrinal_fragments = [f for f in fragments if f["type"] == "doctrina"]
        
        for i, doc1 in enumerate(doctrinal_fragments):
            for doc2 in doctrinal_fragments[i+1:]:
                # Detectar relación basada en keywords comunes
                common_keywords = set(doc1.get("keywords", [])) & set(doc2.get("keywords", []))
                
                if common_keywords:
                    try:
                        await self.knowledge_graph.relate_concepts(
                            concept1=doc1["id"],
                            concept2=doc2["id"],
                            relation_type="RELACION_DOCTRINAL",
                            strength=len(common_keywords) * 0.2
                        )
                        relationship_count += 1
                        print(f"[GRAPH DB] Created relationship: {doc1['id']} ↔ {doc2['id']}")
                    except Exception as e:
                        print(f"[GRAPH DB] Error creating relationship: {e}")
        
        return relationship_count
    
    async def run_full_ingestion(self) -> Dict[str, Any]:
        """Ejecuta el proceso completo de ingestión"""
        print("[KNOWLEDGE INGESTION] Starting full ingestion process...")
        
        # Paso 1: Inicializar servicios
        await self.initialize_services()
        
        # Paso 2: Cargar base de conocimiento
        knowledge_data = await self.load_knowledge_base()
        fragments = knowledge_data["knowledge_base"]["fragments"]
        
        if not fragments:
            print("[KNOWLEDGE INGESTION] No fragments to ingest")
            return self.ingestion_stats
        
        # Paso 3: Ingestar en base vectorial
        print("[KNOWLEDGE INGESTION] Ingesting to Vector DB (Qdrant)...")
        vector_count = await self.ingest_to_vector_db(fragments)
        
        # Paso 4: Ingestar en grafo de conocimiento
        print("[KNOWLEDGE INGESTION] Ingesting to Graph DB (Neo4j)...")
        graph_count = await self.ingest_to_graph_db(fragments)
        
        # Paso 5: Crear relaciones doctrinales
        print("[KNOWLEDGE INGESTION] Creating doctrinal relationships...")
        doctrinal_count = await self.create_doctrinal_relationships(fragments)

        # Paso 6: Puente Sináptico (relaciones por similitud vectorial)
        print("[KNOWLEDGE INGESTION] Building synaptic vector-graph bridges...")
        synaptic_count = await self.create_synaptic_relationships(fragments)

        # Paso 7: Calcular estadísticas finales
        self.ingestion_stats["successful_ingestions"] = max(vector_count, graph_count)
        self.ingestion_stats["doctrinal_relationships"] = doctrinal_count
        self.ingestion_stats["synaptic_relationships"] = synaptic_count
        self.ingestion_stats["relationships_created"] = doctrinal_count + synaptic_count
        
        print("[KNOWLEDGE INGESTION] Ingestion completed successfully!")
        print(f"[KNOWLEDGE INGESTION] Stats: {self.ingestion_stats}")
        
        return self.ingestion_stats
    
    def _prepare_vector_content(self, fragment: Dict[str, Any]) -> str:
        """Prepara el contenido para vectorización"""
        # Combinar contenido con metadata para mejor representación
        content_parts = [
            fragment["content"],
            f"Tipo: {fragment['type']}",
            f"Categoría: {fragment['category']}",
            f"Peso doctrinal: {fragment.get('doctrinal_weight', 0.0)}"
        ]
        return " | ".join(content_parts)
    
    def _extract_entities(self, fragment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrae entidades del fragmento para el grafo"""
        entities = []
        
        # Entidad principal basada en el fragmento
        entities.append({
            "name": fragment["id"],
            "type": fragment["type"],
            "confidence": fragment.get("doctrinal_weight", 0.8),
            "category": fragment["category"]
        })
        
        # Entidades basadas en keywords
        for keyword in fragment.get("keywords", []):
            entities.append({
                "name": keyword,
                "type": "concepto",
                "confidence": 0.7,
                "category": fragment["category"]
            })
        
        return entities[:10]  # Limitar a 10 entidades por fragmento
    
    async def close_services(self):
        """Cierra los servicios cognitivos"""
        if SERVICES_AVAILABLE:
            await self.cognitive_memory.close()
            await self.knowledge_graph.close()
            print("[KNOWLEDGE INGESTION] Services closed successfully")

async def main():
    """Función principal para ejecutar la ingestión"""
    ingestion = KnowledgeIngestion()
    
    try:
        stats = await ingestion.run_full_ingestion()
        print(f"\n[INGESTION COMPLETED] Final statistics: {stats}")
        
    except Exception as e:
        print(f"[KNOWLEDGE INGESTION] Error during ingestion: {e}")
    finally:
        await ingestion.close_services()

if __name__ == "__main__":
    asyncio.run(main())