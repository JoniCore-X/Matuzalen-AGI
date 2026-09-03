# Cognitive Core AGI - Núcleo de Inteligencia General

Sistema cognitivo distribuido que implementa memoria vectorial, grafo de conocimiento y motor de razonamiento para capacidades AGI.

## Arquitectura

### Componentes Principales

1. **Memoria Cognitiva (Qdrant)** - Base de datos vectorial para RAG
2. **Grafo de Conocimiento (Neo4j)** - Sistema de relaciones y entidades
3. **Motor de Razonamiento** - Procesamiento cognitivo y toma de decisiones
4. **API FastAPI** - Interfaz de comunicación con AutoPlan

### Stack Tecnológico

- **Vector DB**: Qdrant (memoria semántica)
- **Graph DB**: Neo4j (relaciones y conocimiento)
- **Cache**: Redis (estado rápido)
- **API**: FastAPI (Python)
- **Embeddings**: SentenceTransformers
- **Orquestación**: Docker Compose

## Instalación y Uso

### Prerrequisitos

- Docker y Docker Compose
- Python 3.8+
- pip

### Inicio Rápido

```bash
# Windows
start-cognitive-system.bat

# Linux/Mac
chmod +x start-cognitive-system.sh
./start-cognitive-system.sh
```

### Manual

```bash
# 1. Iniciar servicios Docker
docker-compose up -d

# 2. Instalar dependencias
cd cognitive-core
pip install -r requirements.txt

# 3. Iniciar API
python main.py
```

## Endpoints API

### Health Check
```
GET /health
```

### Procesar Intención
```
POST /cognitive/process
Content-Type: application/json

{
  "intention": "analizar el progreso del proyecto",
  "context": {"project_id": "123", "timeline": "Q4"},
  "urgency": "medium"
}
```

### Almacenar Conocimiento
```
POST /knowledge/store
Content-Type: application/json

{
  "content": "El proyecto AutoPlan implementa planificación autónoma",
  "type": "project_knowledge",
  "metadata": {"project": "AutoPlan", "category": "documentation"}
}
```

### Buscar Conocimiento
```
GET /knowledge/search?query=planificación autónoma&limit=5
```

## Integración con AutoPlan

El cliente cognitivo en `backend/cognitive-client.ts` se comunica con este servicio:

```typescript
import { cognitiveClient } from './cognitive-client';

const response = await cognitiveClient.processIntention({
  intention: "optimizar tareas del proyecto",
  context: { projectId: "123" },
  urgency: "medium"
});
```

## Arquitectura de Memoria

### Memoria Semántica (Qdrant)
- Almacena embeddings de todo el conocimiento
- Búsqueda por similitud semántica
- Recuperación aumentada (RAG)

### Grafo de Conocimiento (Neo4j)
- Relaciones entre entidades y conceptos
- Razonamiento lógico y deducción
- Navegación de conocimiento estructurado

## Desarrollo

### Estructura de Proyecto

```
cognitive-core/
├── main.py              # API FastAPI principal
├── cognitive_memory.py  # Sistema de memoria vectorial
├── knowledge_graph.py   # Sistema de grafo de conocimiento
├── reasoning_engine.py  # Motor de razonamiento
├── requirements.txt     # Dependencias Python
└── .env                # Configuración
```

### Extensión

Para agregar nuevas capacidades cognitivas:

1. Extender `ReasoningEngine` con nuevos algoritmos
2. Agregar endpoints en `main.py`
3. Integrar nuevas fuentes de conocimiento en `CognitiveMemory`

## Monitoreo

- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, pass: ultron_cognitive_2026)
- **API Docs**: http://localhost:8000/docs

## Roadmap

- [ ] Integración con LLMs avanzados (GPT-4, Claude)
- [ ] Aprendizaje continuo y auto-mejora
- [ ] Sandbox de ejecución segura (WebAssembly)
- [ ] Sistema de eventos (Kafka/Redpanda)
- [ ] Multi-agent orquestation
- [ ] Optimización de rendimiento con Rust

## Seguridad

- Aislamiento de contenedores Docker
- Autenticación en bases de datos
- Validación de entrada en API
- Límites de seguridad en razonamiento

## Licencia

Sistema cognitivo para proyecto AGI - Uso interno confidencial.