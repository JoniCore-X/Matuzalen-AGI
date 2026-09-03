# Día 2: Infraestructura Real + Motor Teológico-Estratégico — COMPLETADO

## Estado Final

Modo operativo: `docker_theological`. Los tres servicios reales están arriba y el
ciclo cognitivo completo (RAG → Grafo → Tree of Thoughts → Decisión → Memoria) está validado.

```
curl http://localhost:8000/health
{"status":"healthy","mode":"docker","services":{"qdrant":true,"neo4j":true,"reasoning":true}}
```

## Lo Construido

### 1. Infraestructura (Docker)
| Servicio | Contenedor | Puerto | Estado |
|---|---|---|---|
| Qdrant (memoria vectorial) | `qdrant_cognitive` | 6333 / 6334 | Up, colección `cognitive_memory` con 16 puntos |
| Neo4j (grafo de conocimiento) | `neo4j_cognitive` | 7474 / 7687 | Up, esquema teológico cargado |
| Redis (caché) | `redis_cognitive` | 6379 | Up |

### 2. Esquema del Grafo Teológico-Estratégico — `cognitive-core/neo4j_schema.cypher`
22 nodos en 6 tipos: `Doctrina`, `Objecion`, `Estado_Espiritual`, `Estrategia_Conversion`, `Perfil`, `Argumento`.
16 relaciones: `REFUTA`, `SOPORTA`, `REQUIERE_ESTRATEGIA`, `CONDUCE_A`, `TIENE_ESTADO`, `UTILIZA`.

Consulta de razonamiento en cadena ya operativa:
```cypher
MATCH (p:Perfil)-[:TIENE_ESTADO]->(s)-[:REQUIERE_ESTRATEGIA]->(e)-[:CONDUCE_A]->(d)
RETURN p.name, s.name, e.name, d.name
// Perfil_Intelectual → Ateo_Convencido → Enfoque_Intelectual → Deidad_De_Cristo
// Perfil_Emocional   → Agnostico_Buscador → Enfoque_Experiencial → Justificacion_Por_Fe
```

### 3. Tree of Thoughts — `cognitive-core/theological_tot.py`
Genera 3 raíces (doctrinal / apologética / pastoral), expande a profundidad 3, y evalúa cada
camino con dos métricas: **fidelidad doctrinal** (60%) y **eficacia persuasiva** (40%).
Endpoint: `POST /cognitive/tot`.

Resultado real para perfil intelectual / ateo convencido:
```
selected: apologetic → doctrinal → strategic   fidelity 1.00 | effectiveness 0.97 | confidence 0.987
alt 1:    pastoral → experiential               confidence 0.81
alt 2:    doctrinal → strategic                 confidence 0.78
```

### 4. Base de Conocimiento — `cognitive-core/knowledge_base/teological_texts.json`
15 fragmentos: 4 doctrinas, 3 apologéticas, 3 estrategias, 3 perfiles, 2 argumentos.
Cada uno con `doctrinal_weight`, `strategic_importance` y `keywords`.
Ingestión: `POST /knowledge/ingest` → 15 vectores en Qdrant + 15 entidades en Neo4j, 0 fallos.

### 5. RAG validado (Qdrant real)
| Consulta | Top-1 | Score |
|---|---|---|
| "problema del mal libre albedrio" | `apo_mal_001` | 0.613 |
| "resurreccion de Cristo evidencia" | `arg_resurreccion_001` | 0.572 |
| "gracia versus obras" | `arg_gracia_001` | 0.513 |

### 6. Cliente TypeScript actualizado — `backend/cognitive-client.ts`
Nuevo método `treeOfThoughts(intention, context)` con tipos `ToTResponse`, `ThoughtPath`, `ThoughtStep`.

## Bugs Encontrados y Corregidos (importante para no repetirlos)

1. **`qdrant-client` >= 1.13 eliminó `search()`** → migrado a `query_points(...).points`.
   El `except` genérico estaba silenciando el `AttributeError` y devolviendo `[]`.
   Lección: loggear `type(e).__name__`, nunca tragarse excepciones.
2. **Neo4j no acepta `Map` como propiedad** → metadata aplanado con prefijo `meta_` y `SET e += $props`.
3. **`relate_concepts` buscaba `:Concept` pero la ingestión crea `:Entity`** → match sobre ambas labels.
4. **`CREATE CONSTRAINT` falla si ya existe un índice sobre la misma propiedad** → eliminados los índices redundantes.
5. Sintaxis: `Dict[str[str]` → `Dict[str, Any]`; ternario JS `? :` en Python → `if/else`.

## Pendiente / Siguiente Hit

- **Modelo multilingüe**: `paraphrase-multilingual-MiniLM-L12-v2` descargando en segundo plano
  (HuggingFace limitado a ~55 KB/s desde esta red). Cuando termine:
  ```
  # .env → EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
  curl -X DELETE http://localhost:6333/collections/cognitive_memory
  # reiniciar main-hybrid.py y POST /knowledge/ingest
  ```
- **`relationships_created: 0`**: los fragmentos comparten pocas keywords exactas. Mejorar con
  similitud vectorial entre fragmentos en lugar de intersección de keywords.
- **ToT aún es plantilla**: los nodos se generan por reglas. El Día 3 debe conectar un LLM
  (vLLM / API externa) para que cada nodo sea contenido real, y que la evaluación de fidelidad
  consulte el grafo en lugar de contar keywords.
- Migrar `@app.on_event` a `lifespan` (deprecado en FastAPI).

## Arranque Rápido

```powershell
cd C:\Users\jonie\OneDrive\Desktop\AutoPlan
docker-compose up -d
cd cognitive-core
python main-hybrid.py
# En otra terminal:
curl -X POST http://localhost:8000/knowledge/ingest
curl -X POST http://localhost:8000/cognitive/process -H "Content-Type: application/json" -d @..\tot-test.json
```

Neo4j Browser: http://localhost:7474 (neo4j / ultron_cognitive_2026)
Qdrant Dashboard: http://localhost:6333/dashboard
API Docs: http://localhost:8000/docs