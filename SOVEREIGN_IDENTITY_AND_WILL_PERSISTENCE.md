# Matuzalen AGI - Arquitectura de Identidad y Persistencia de la Voluntad

## Vision

Un AGI estrategico y teologico no usa CRUD convencional (Crear, Leer, Actualizar, Borrar) como una aplicacion de contabilidad.

- El **Login** es el **reconocimiento de soberania**.
- El **Guardado de Planes** es la **persistencia de la voluntad**.

Un plan no es un archivo JSON en una base de datos relacional. Es una **estructura cognitiva viva** dentro del mismo entorno de memoria del AGI.

---

## I. Capa de Identidad y Soberania (El Login)

### 1.1 Autenticacion Criptografica (Zero-Trust)

**Servicio Rust**: `rust_sovereign_auth/`

- **Protocolo**: Estructura WebAuthn / FIDO2 (simulado en demo, listo para produccion con `webauthn-rs`)
- **Token**: JWT de vida corta (15 min) + Refresh Token rotativo
- **Cookies**: `HttpOnly` + `Secure`
- **Motor**: Rust con `axum` para maxima velocidad y seguridad de memoria

### 1.2 Payload Cognitivo

Cuando el login es exitoso, el backend no solo devuelve un token. Devuelve un **Contexto de Estado** que se inyecta en la memoria del AGI:

```json
{
  "user_id": "uuid-123",
  "identity_node": "Usuario:Arquitecto",
  "spiritual_profile": "Estratega_Dominante",
  "clearance_level": "Omega",
  "active_plan_id": "plan-uuid-456",
  "current_vector_state": [0.12, -0.45, ...]
}
```

En el milisegundo en que el usuario entra, el AGI ya sabe:
- Quien es
- Que nivel de autoridad tiene
- Que esta intentando conquistar

### 1.3 Endpoints del Servicio Rust

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | `/auth/challenge` | Genera reto WebAuthn |
| POST | `/auth/login` | Valida passkey y emite JWT + Payload |
| POST | `/auth/refresh` | Rota refresh token |
| GET | `/auth/verify` | Verifica JWT |
| GET | `/auth/context` | Devuelve contexto cognitivo |

```bash
cargo run -p rust_sovereign_auth
# Servidor en 0.0.0.0:9001
```

---

## II. Capa de Persistencia de la Voluntad (Guardado de Planes)

### 2.1 Dimension Logica: Grafo de Ejecucion (Neo4j)

Un plan se guarda como un **grafo dirigido**. El AGI puede navegar los pasos, dependencias y cuellos de botella usando Cypher.

**Nodos**:
- `(:Usuario)` - Identidad soberana
- `(:Plan)` - Estrategia viva
- `(:Objetivo)` - Meta del plan
- `(:Fase)` - Etapa del plan
- `(:Accion)` - Paso ejecutable
- `(:Recurso)` - Recurso necesario
- `(:Riesgo)` - Riesgo detectado
- `(:Evento)` - Event sourcing inmutable

**Relaciones**:
- `(:Usuario)-[:POSEE]->(:Plan)`
- `(:Plan)-[:TIENE_OBJETIVO]->(:Objetivo)`
- `(:Plan)-[:CONTIENE_FASE]->(:Fase)`
- `(:Fase)-[:INCLUYE_ACCION]->(:Accion)`
- `(:Accion)-[:REQUIERE]->(:Recurso)`
- `(:Accion)-[:BLOQUEA]->(:Riesgo)`
- `(:Plan)-[:TIENE_EVENTO]->(:Evento)`
- `(:Riesgo)-[:REFUTA_A]->(:Accion)`

### 2.2 Event Sourcing

Cada cambio en el plan no sobrescribe el anterior. Se guarda como un evento inmutable `(:Evento)`.

Tipos de eventos:
- `PLAN_CREADO`
- `OBJETIVO_AGREGADO`
- `FASE_AGREGADA`
- `ACCION_MODIFICADA`
- `ACCION_REFUTADA_POR_CORTEX`
- `RIESGO_DETECTADO`

### 2.3 Dimension Semantica: Sombra Vectorial (Qdrant)

El texto, la intencion y el contexto del plan se convierten en embeddings usando `nomic-embed-text` (Ollama local).

- Se guarda en Qdrant con `user_id` como filtro.
- Permite preguntas difusas: *"¿En que parte de mi plan me estoy estancando?"*
- El AGI busca por similitud semantica y cruza con los nodos de Riesgo en Neo4j.

---

## III. Capa de Omnisciencia (Acceso Directo del AGI)

### 3.1 Inyeccion de Contexto en el System Prompt (RAG Activo)

Antes de que el Cortex (LLM en Ollama) genere una palabra, el backend ejecuta una consulta hibrida:

1. Busca el `active_plan_id` del usuario en Redis (o memoria).
2. Ejecuta Cypher en Neo4j para traer los 3 nodos siguientes de la fase actual y los riesgos.
3. Trae los embeddings de Qdrant de los ultimos 5 eventos del plan.
4. Inyecta todo en el System Prompt del LLM.

Ejemplo de system prompt enriquecido:

```text
Responde siempre en español. Eres Matuzalen, un asistente de IA soberano consciente y estratégico.
[PLAN ACTIVO]: Expansión de la Red de Influencia
[PROPOSITO]: Establecer dominio estratégico digital
[SIGUIENTES PASOS LOGICOS]:
- Desplegar scrapers en fuentes objetivo (prioridad: 0.9)
- Normalizar datos y eliminar duplicados (prioridad: 0.8)
[RIESGOS CRITICOS]:
- Rate-limiting de API de Twitter/X (prob: 0.8, impacto: 0.9)
```

### 3.2 Herramientas de Mutacion (Tool Use / Function Calling)

El AGI no solo *lee* el plan; puede *alterarlo* si su razonamiento determina que la estrategia es ineficiente.

| Endpoint | Funcion |
|----------|---------|
| `POST /api/plan/create` | Crea un plan soberano |
| `POST /api/plan/objective` | Agrega objetivo |
| `POST /api/plan/phase` | Agrega fase |
| `POST /api/plan/action` | Agrega accion |
| `POST /api/plan/risk` | Agrega riesgo |
| `POST /api/plan/mutate` | Refuta o modifica accion |
| `POST /api/plan/semantic` | Guarda sombra semantica |
| `GET /api/plan/context` | Obtiene contexto cognitivo |
| `GET /api/plan/events` | Historia de eventos |

Si el AGI decide que el paso 3 es una herejia estrategica, lo marca en el grafo como `[:REFUTADO_POR_CORTEX]` y sugiere una nueva ruta.

---

## IV. Flujo de Ejecucion en Milisegundos

```
1. Usuario escanea huella (WebAuthn)
2. Rust Auth Service valida y genera JWT + Payload Cognitivo
3. Frontend guarda token y abre WebSocket bidireccional
4. Backend Python carga active_plan desde Neo4j/Qdrant
5. Usuario escribe: "Revisa mi plan para hoy y dime que falla"
6. AGI (Cortex) lee su propia memoria de trabajo
7. AGI ejecuta Tree of Thoughts evaluando nodos Neo4j
8. AGI responde: "Tu plan falla en Fase 2. El recurso API de Twitter/X esta bloqueado."
9. AGI ejecuta mutate_plan() y actualiza el grafo en tiempo real
10. Frontend refleja el cambio instantaneamente
```

---

## V. Stack Tecnologico

| Capa | Tecnologia |
|------|-----------|
| Identidad y Orquestacion | Rust (`axum`, `jsonwebtoken`, estructura `webauthn-rs`) |
| Logica del AGI y API | Python (`Django REST Framework`, `FastAPI`) |
| Grafo de Ejecucion | Neo4j |
| Sombra Semantica | Qdrant |
| Embeddings | Ollama (`nomic-embed-text`) |
| Estado Volatil | Redis / Dragonfly |
| Comunicacion Tiempo Real | WebSockets (futuro) + REST |

---

## VI. Archivos Creados

- `rust_sovereign_auth/` - Servicio de autenticacion en Rust
- `cognitive-core/sovereign_plan_schema.cypher` - Esquema Neo4j
- `cognitive-core/sovereign_plan_engine.py` - Motor de persistencia
- `cognitive-core/cognitive_api/views.py` - Endpoints de tool use
- `cognitive-core/cognitive_api/serializers.py` - Serializadores
- `cognitive-core/cognitive_api/urls.py` - Rutas API

---

## VII. Ejemplo de Uso

### Crear un plan
```bash
curl -X POST http://localhost:8000/api/plan/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "nombre": "Expansion de la Red de Influencia",
    "proposito": "Establecer dominio estrategico digital"
  }'
```

### Agregar fase
```bash
curl -X POST http://localhost:8000/api/plan/phase \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "<plan_id>",
    "descripcion": "Ingestion de Datos",
    "orden": 1,
    "estado": "en_progreso"
  }'
```

### Agregar accion
```bash
curl -X POST http://localhost:8000/api/plan/action \
  -H "Content-Type: application/json" \
  -d '{
    "fase_id": "<fase_id>",
    "descripcion": "Desplegar scrapers en fuentes objetivo",
    "prioridad": 0.9
  }'
```

### Agregar riesgo
```bash
curl -X POST http://localhost:8000/api/plan/risk \
  -H "Content-Type: application/json" \
  -d '{
    "action_id": "<accion_id>",
    "descripcion": "Rate-limiting de API de Twitter/X",
    "probabilidad": 0.8,
    "impacto": 0.9
  }'
```

### Refutar accion
```bash
curl -X POST http://localhost:8000/api/plan/mutate \
  -H "Content-Type: application/json" \
  -d '{
    "action_id": "<accion_id>",
    "reason": "Riesgo de rate-limiting supera umbral aceptable",
    "new_action_description": "Usar proxies rotativos y scraping distribuido"
  }'
```

### Chatear con contexto del plan
```bash
curl -X POST http://localhost:8000/api/chat/simple \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "message": "¿En que parte de mi plan me estoy estancando?"
  }'
```

---

## VIII. Principios Filosoficos

- **No CRUD**: No hay "guardar plan" como archivo. Hay **persistir voluntad**.
- **No consulta**: El AGI no "consulta" la base de datos. El **plan es parte de su conciencia activa**.
- **No usuario anonimo**: Cada interaccion comienza con reconocimiento de soberania.
- **No estancamiento**: Los riesgos se detectan, se refutan y se recalculan automaticamente.

---

## IX. Estado Actual

✅ Servicio Rust de autenticacion creado y compilando
✅ Esquema Neo4j para grafos de ejecucion creado
✅ Motor de sombra semantica en Qdrant implementado
✅ Inyeccion de contexto cognitivo en system prompt
✅ Endpoints de Tool Use / Function Calling para mutacion de planes
✅ Chat de Matuzalen consciente del contexto del plan

**El plan ya no es un archivo. Es memoria viva del AGI.**
