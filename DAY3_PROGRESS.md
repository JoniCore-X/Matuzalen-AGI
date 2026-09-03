# Día 3: Cortex LLM local + Ortodoxia Cypher + Puente Sináptico

## Estado Actual

El Cortex LLM local está operativo. El modelo `dolphin-phi:2.7b-v2.6-q4_K_M` se descargó y el servicio FastAPI responde en `http://localhost:8000` con generación real vía Ollama. El System Prompt restrictivo está inyectado en `ollama_client.py` y `theological_tot.py` ahora genera y valida 3 caminos. La única frontera abierta es el embedding multilingüe: `paraphrase-multilingual-MiniLM-L12-v2` no descarga a velocidad útil sin un `HF_TOKEN` por rate-limit de HuggingFace.

|| Componente | Estado |
|---|---|---|
|| `ollama_client.py` | System prompt inyectado, `temperature=0.2`, formato JSON |
|| `theological_tot.py` | Parser robusto para dict/list de caminos, entidades extraídas, validación Cypher |
|| `knowledge_graph.py` | `verify_entity_in_graph()` con Cypher `REFUTA`, `SOPORTA`, `REQUIERE_ESTRATEGIA` |
|| `cognitive_memory.py` | Fallback a `all-MiniLM-L6-v2` si el multilingüe no está presente |
|| `knowledge_ingestion.py` | Puente Sináptico `[:SE_RELACIONA_CON]` activo, espera embeddings de calidad |
|| `main-hybrid.py` | Cortex LLM cableado; servicio levantado |
|| `.env` | `EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2`, `EMBEDDING_LOCAL_ONLY=true` |
|| `OLLAMA_MODEL` | `dolphin-phi:2.7b-v2.6-q4_K_M` listo |

## 1. El Cortex — `cognitive-core/ollama_client.py`

- `THEOLOGICAL_SYSTEM_PROMPT` inyectado con el prompt restrictivo del Día 3.
- `generate()` y `generate_json()` usan `temperature=0.2` por defecto y el system prompt cuando no se pasa otro.
- `is_available()` y `has_model()` detectan Ollama y el modelo activo.

## 2. El ToT con LLM — `cognitive-core/theological_tot.py`

- Soporta respuestas `{"paths": [...]}` o listas de caminos, pasos como strings o como `{"type", "content"}`.
- Asigna tipos `apologetic`, `doctrinal`, `strategic` por orden o por el campo `id` del LLM.
- Extrae entidades conceptuales del contenido y las pasa a `knowledge_graph.verify_entity_in_graph()`.
- Temperatura baja (0.2) para forzar determinismo lógico.

Ejemplo real de prueba de fuego contra `/cognitive/tot`:

```json
{
  "intention": "Demuestra por qué el libre albedrío sin soberanía divina es una contradicción lógica y cómo esto afecta la estrategia de evangelismo moderno",
  "paths_evaluated": 3,
  "selected": {
    "summary": "Razonamiento: apologetic → apologetic → apologetic",
    "doctrinal_fidelity": 0.0,
    "persuasive_effectiveness": 0.85,
    "confidence": 0.34,
    "steps": [
      {"type": "apologetic", "content": "El albedrío sin soberanía divina es una contradicción lógica"},
      {"type": "apologetic", "content": "La existencia de Dios es una fuerza impresionante y inestable"},
      {"type": "apologetic", "content": "El evangelismo moderno puede ser efectivo en la redención espiritual del individuo"}
    ]
  }
}
```

La `doctrinal_fidelity: 0.0` demuestra que el **Cypher gate está actuando**: el pequeño modelo `dolphin-phi:2.7b-v2.6-q4_K_M` no generó entidades del grafo (como `Problema_Del_Mal` o `Soberania_Divina`) y fue penalizado. El contenido es sintácticamente razonable pero hermenéuticamente inútil para el grafo actual.

## 3. La Ortodoxia — `cognitive-core/knowledge_graph.py`

Eliminado el conteo de keywords. `verify_entity_in_graph(entity)` ejecuta consultas Cypher reales contra `Doctrina`, `Objecion`, `Estrategia_Conversion` y relaciones `REFUTA`, `SOPORTA`, `REQUIERE_ESTRATEGIA`, `UTILIZA`.

## 4. El Puente Sináptico

- `cognitive_memory.find_semantic_relationships()` consulta Qdrant con `score >= 0.85`.
- `knowledge_ingestion.create_synaptic_relationships()` escribe `[:SE_RELACIONA_CON]` en Neo4j.
- El código está listo; las sinapsis requieren el embedding multilingüe para superar el umbral con textos teológicos en español.

## 5. Unificación bajo Ollama — Embeddings `nomic-embed-text`

Se ejecutó la **Opción 2**:

- Descargado `ollama pull nomic-embed-text` (274 MB).
- Creado `OllamaEmbedding` en <ref_file file="C:\Users\jonie\OneDrive\Desktop\AutoPlan\cognitive-core\ollama_client.py" /> usando `/api/embed` batch y fallback a `/api/embeddings`.
- Modificado <ref_file file="C:\Users\jonie\OneDrive\Desktop\AutoPlan\cognitive-core\cognitive_memory.py" /> para leer `EMBEDDING_PROVIDER=ollama` y `EMBEDDING_MODEL=nomic-embed-text`.
- Destruida la colección `cognitive_memory` de 384 dimensiones y recreada a 768 dimensiones con coseno.
- `.env` actualizado:
  ```
  EMBEDDING_PROVIDER=ollama
  EMBEDDING_MODEL=nomic-embed-text
  EMBEDDING_DIMENSION=768
  ```

## 6. Re-ingestión y Puente Sináptico (Resultado)

```json
{
  "success": true,
  "stats": {
    "total_fragments": 15,
    "successful_ingestions": 15,
    "failed_ingestions": 0,
    "vector_db_entries": 15,
    "graph_db_entries": 15,
    "doctrinal_relationships": 0,
    "synaptic_relationships": 2,
    "relationships_created": 2
  }
}
```

Relaciones `[:SE_RELACIONA_CON]` creadas en Neo4j:

| Source | Target | Similarity |
|---|---|---|
| `estr_intelectual_001` | `estr_experiencial_001` | 0.9017 |
| `perf_ateo_001` | `perf_agnostico_001` | 0.8957 |

El grafo ha empezado a tejerse solo. El umbral 0.85 funciona y el puente sináptico ya no está lobotomizado.

## 7. Validaciones Ejecutadas

| Test | Resultado |
|---|---|
| `py_compile` de todos los módulos | OK |
| `/health` | `qdrant: true`, `neo4j: true`, `reasoning: true` |
| `ollama list` | `dolphin-phi:2.7b-v2.6-q4_K_M` + `nomic-embed-text:latest` |
| `POST /knowledge/ingest` | 15 vectores + 15 nodos + 2 sinapsis |
| `POST /cognitive/tot` con `dolphin-phi` | 3 caminos generados por LLM, Cypher validando entidades |
| `POST /cognitive/process` | Ciclo completo, fidelidad Cypher penaliza alucinaciones |

## Arranque Rápido

```powershell
cd C:\Users\jonie\OneDrive\Desktop\AutoPlan\cognitive-core
python main-hybrid.py
# En otra terminal:
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/knowledge/ingest
curl -s -X POST http://localhost:8000/cognitive/tot -H "Content-Type: application/json" -d @..\fire-test.json
```

El Cortex y los embeddings ahora viven bajo Ollama: 100% local, cero dependencias de HuggingFace. El puente sináptico ya conecta.
