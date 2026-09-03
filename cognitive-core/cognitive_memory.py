"""
Memoria Cognitiva - Sistema de Memoria Vectorial
Implementa RAG (Retrieval-Augmented Generation) usando Qdrant
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
import os
from typing import List, Dict, Any, Optional, Union
import asyncio
from datetime import datetime
from ollama_client import OllamaEmbedding

class CognitiveMemory:
    def __init__(self):
        self.qdrant_client = None
        self.embedding_model = None
        self.collection_name = "cognitive_memory"
        self.initialized = False

    async def initialize(self):
        """Inicializa la conexión con Qdrant y el modelo de embeddings"""
        try:
            # Conectar con Qdrant
            self.qdrant_client = QdrantClient(
                host="localhost",
                port=6333,
                timeout=60
            )

            # Solo usamos Ollama local (100% IA propia)
            model_name = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
            host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            dimension = int(os.getenv("EMBEDDING_DIMENSION", "768"))
            self.embedding_model = OllamaEmbedding(model=model_name, host=host, dimension=dimension)
            print(f"[COGNITIVE MEMORY] Ollama embedding model: {model_name} ({dimension}d) - 100% LOCAL")

            # Crear/recreate colección con la dimensión correcta
            self._ensure_collection_exists()
            
            self.initialized = True
            print("[COGNITIVE MEMORY] Initialized successfully")
            
        except Exception as e:
            print(f"[COGNITIVE MEMORY] Initialization error: {e}")
            raise

    def _get_embedding_dimension(self) -> int:
        if hasattr(self.embedding_model, "get_sentence_embedding_dimension"):
            return self.embedding_model.get_sentence_embedding_dimension()
        # SentenceTransformer usa encode + shape
        sample = "test"
        vec = self._as_list(self.embedding_model.encode(sample))
        return len(vec)

    def _as_list(self, embedding: Any) -> List[float]:
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        if isinstance(embedding, list):
            return list(embedding)
        return list(embedding)

    def _ensure_collection_exists(self):
        """Asegura que la colección existe en Qdrant con la dimensión correcta"""
        collections = self.qdrant_client.get_collections().collections
        collection_names = [col.name for col in collections]
        dimension = self._get_embedding_dimension()
        
        if self.collection_name in collection_names:
            # Si la dimensión cambió, destruir y recrear (los vectores viejos son basura)
            info = self.qdrant_client.get_collection(self.collection_name)
            existing_size = info.config.params.vectors.size
            if existing_size != dimension:
                print(f"[COGNITIVE MEMORY] Collection dimension mismatch ({existing_size} vs {dimension}), deleting old collection")
                self.qdrant_client.delete_collection(self.collection_name)
                collection_names.remove(self.collection_name)
        
        if self.collection_name not in collection_names:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE
                )
            )
            print(f"[COGNITIVE MEMORY] Created collection: {self.collection_name} with dimension {dimension}")

    async def store_knowledge(self, content: str, knowledge_type: str, metadata: Optional[Dict] = None) -> str:
        """Almacena conocimiento en la memoria vectorial"""
        try:
            # Generar embedding
            embedding = self._as_list(self.embedding_model.encode(content))
            
            # Crear punto para Qdrant
            point_id = self._generate_point_id()
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": content,
                    "type": knowledge_type,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Almacenar en Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return str(point_id)
            
        except Exception as e:
            print(f"[COGNITIVE MEMORY] Error storing knowledge: {e}")
            raise

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca conocimiento relevante usando similitud vectorial"""
        try:
            # Generar embedding de la consulta
            query_embedding = self._as_list(self.embedding_model.encode(query))
            
            # Buscar en Qdrant (API query_points; search() fue eliminado en qdrant-client >= 1.13)
            search_results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit,
                score_threshold=0.25  # Umbral de similitud (MiniLM-L6 es débil en español; subir al migrar a modelo multilingüe)
            ).points
            
            # Formatear resultados
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload["content"],
                    "type": result.payload["type"],
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() 
                               if k not in ["content", "type"]},
                    "timestamp": result.payload.get("timestamp", "")
                })
            
            return results
            
        except Exception as e:
            print(f"[COGNITIVE MEMORY] Error searching: {type(e).__name__}: {e}")
            return []

    async def find_semantic_relationships(self, content: str, own_id: str,
                                          threshold: float = 0.85, limit: int = 5) -> List[Dict[str, Any]]:
        """Encuentra puntos Qdrant con similitud de coseno >= threshold, excluyendo el propio."""
        try:
            query_embedding = self._as_list(self.embedding_model.encode(content))
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit + 5,
                with_payload=True,
                score_threshold=threshold
            ).points

            related = []
            for r in results:
                payload = r.payload or {}
                other_id = payload.get("id")
                if other_id == own_id or r.score >= 0.999:
                    continue
                related.append({
                    "id": other_id,
                    "score": round(float(r.score), 4),
                    "content": payload.get("content", ""),
                    "metadata": {k: v for k, v in payload.items() if k not in ["content"]}
                })
            return related[:limit]
        except Exception as e:
            print(f"[COGNITIVE MEMORY] Error finding semantic relationships: {type(e).__name__}: {e}")
            return []

    async def store_interaction(self, intention: str, decision: Dict[str, Any]) -> str:
        """Almacena interacciones para aprendizaje"""
        try:
            interaction_content = f"Intention: {intention} | Decision: {decision.get('action', '')}"
            return await self.store_knowledge(
                content=interaction_content,
                knowledge_type="interaction",
                metadata={
                    "intention": intention,
                    "decision": decision,
                    "confidence": decision.get("confidence", 0)
                }
            )
        except Exception as e:
            print(f"[COGNITIVE MEMORY] Error storing interaction: {e}")
            return ""

    def _generate_point_id(self) -> int:
        """Genera un ID único para el punto"""
        return int(datetime.now().timestamp() * 1000000)

    def is_healthy(self) -> bool:
        """Verifica si el servicio está saludable"""
        try:
            if not self.initialized or not self.qdrant_client:
                return False
            self.qdrant_client.get_collections()
            return True
        except:
            return False

    async def close(self):
        """Cierra la conexión"""
        if self.qdrant_client:
            self.qdrant_client.close()
        print("[COGNITIVE MEMORY] Connection closed")