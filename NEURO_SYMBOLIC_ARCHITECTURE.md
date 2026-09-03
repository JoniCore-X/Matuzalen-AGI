# Arquitectura Neuro-Simbólica Híbrida - AutoPlan AGI

## Visión General

AutoPlan ha evolucionado a una arquitectura cognitiva neuro-simbólica que integra todos los paradigmas clásicos y modernos de IA en un sistema unificado, sin alucinaciones y con determinismo garantizado donde sea posible.

## Paradigmas Implementados

### 1. Neuronas Artificiales (Conexionismo/Deep Learning)
**Archivo**: `neural_networks.py`

- **Redes Neuronales**: Implementación de redes neuronales desde cero
- **Tipos de Capas**: Dense, Convolutional, Recurrent, Attention
- **Funciones de Activación**: Sigmoid, ReLU, Tanh, Softmax
- **Entrenamiento**: Backpropagation con optimización
- **Reconocimiento de Patrones**: Clasificación y reconocimiento
- **Componentes**:
  - `NeuralNetwork`: Red neuronal base
  - `PatternRecognizer`: Reconocedor de patrones
  - `DeepLearningEngine`: Motor de gestión de redes

**Uso**: Reconocimiento de patrones, clasificación, aprendizaje supervisado.

### 2. IA Simbólica (Lógica/Símbolos/GOFAI)
**Archivo**: `symbolic_ai.py`

- **Símbolos Lógicos**: Constantes, variables, predicados, funciones
- **Operadores Lógicos**: AND, OR, NOT, IMPLIES, IFF, FORALL, EXISTS
- **Inferencia**: Encadenamiento hacia adelante y atrás
- **Resolución**: Algoritmo de resolución para lógica proposicional
- **Sistemas Expertos**: Base de conocimiento con reglas
- **Componentes**:
  - `SymbolicReasoner`: Motor de razonamiento simbólico
  - `ExpertSystem`: Sistema experto por dominio
  - `LogicSolver`: Solucionador de problemas lógicos

**Uso**: Razonamiento lógico formal, sistemas expertos, validación de consistencia.

### 3. Memoria Asociativa Vectorial
**Archivo**: `associative_memory.py`

- **Red de Hopfield**: Memoria asociativa auto-organizada
- **Memoria Bidireccional (BAM)**: Asociación bidireccional de patrones
- **Memoria Direccionable por Contenido**: Recuperación por similitud vectorial
- **Almacenamiento**: Patrones con etiquetas y metadatos
- **Recuperación**: Recuerdo asociativo y búsqueda por similitud
- **Componentes**:
  - `HopfieldNetwork`: Red de Hopfield
  - `BidirectionalMemory`: Memoria bidireccional
  - `ContentAddressableMemory`: Memoria direccionable
  - `AssociativeMemoryEngine`: Motor de gestión

**Uso**: Memoria a largo plazo, recuperación de patrones, asociación semántica.

### 4. Algoritmos Deterministas (Código Clásico)
**Archivo**: `deterministic_algorithms.py`

- **Búsqueda**: Búsqueda binaria, búsqueda lineal
- **Ordenamiento**: QuickSort, MergeSort
- **Búsqueda de Caminos**: Dijkstra, A*
- **Optimización**: Programación dinámica (mochila), greedy
- **Planificación**: Round Robin, SJF
- **Clasificación**: K-Nearest Neighbors, Árboles de decisión
- **Determinismo**: Sin aleatoriedad, resultados reproducibles
- **Componentes**:
  - `DeterministicSearch`: Algoritmos de búsqueda
  - `DeterministicSorting`: Algoritmos de ordenamiento
  - `DeterministicPathfinding`: Algoritmos de caminos
  - `DeterministicOptimization`: Algoritmos de optimización
  - `DeterministicScheduling`: Algoritmos de planificación
  - `DeterministicClassification`: Algoritmos de clasificación
  - `DeterministicAlgorithmEngine`: Motor de gestión

**Uso**: Cálculos exactos, planificación, optimización, clasificación determinista.

### 5. LLM (Large Language Models)
**Archivo**: `ollama_client.py` (existente)

- **Modelo Local**: `dolphin-phi:2.7b-v2.6-q4_K_M` (actual)
- **Embeddings**: `nomic-embed-text` (Ollama)
- **Generación**: Generación de texto local
- **Tree of Thoughts**: Generación de múltiples caminos de razonamiento
- **Validación**: Integrado con sistema anti-alucinaciones
- **Componentes**:
  - `OllamaClient`: Cliente Ollama
  - `OllamaEmbedding`: Cliente de embeddings
  - `TheologicalToT`: Motor Tree of Thoughts teológico

**Uso**: Generación de texto, razonamiento complejo, explicación, síntesis.

### 6. Grafos
**Archivo**: `knowledge_graph.py` (existente)

- **Neo4j**: Base de datos de grafos
- **Entidades**: Nodos con etiquetas (Doctrina, Argumento, Estrategia)
- **Relaciones**: REFUTA, SOPORTA, REQUIERE_ESTRATEGIA, SE_RELACIONA_CON
- **Validación**: Cypher Gate para validar entidades del LLM
- **Componentes**:
  - `KnowledgeGraph`: Motor de gestión de grafos
  - `Neo4j`: Cliente Neo4j

**Uso**: Representación de conocimiento, validación doctrinal, relaciones conceptuales.

### 7. Sistema Anti-Alucinaciones
**Archivo**: `anti_hallucination.py`

- **Validación Factual**: Contradiciones con base de conocimiento
- **Validación Lógica**: Consistencia lógica entre afirmaciones
- **Validación Numérica**: Verificación de datos numéricos
- **Validación de Memoria**: Consistencia con memoria asociativa
- **Corrección**: Corrección automática de alucinaciones
- **Componentes**:
  - `AntiHallucinationSystem`: Sistema de validación
  - `HallucinationCorrector`: Corrector de respuestas LLM
  - `ValidationReport`: Reporte de validación

**Uso**: Validación de salidas LLM, corrección de errores, garantía de veracidad.

## Arquitectura Híbrida Neuro-Simbólica

### Motor de Integración
**Archivo**: `neuro_symbolic_hybrid.py`

El `NeuroSymbolicEngine` integra todos los paradigmas:

```
┌─────────────────────────────────────────────────────────────┐
│         NeuroSymbolicEngine (Motor de Integración)           │
├─────────────────────────────────────────────────────────────┤
│  Prioridades de Paradigmas:                                 │
│  - Determinista: 0.95 (máxima prioridad)                  │
│  - Simbólico: 0.90 (alta prioridad)                        │
│  - Grafos: 0.85 (alta prioridad)                            │
│  - Memoria Asociativa: 0.80                                │
│  - Deep Learning: 0.70                                       │
│  - LLM: 0.60 (baja prioridad, validado)                     │
└─────────────────────────────────────────────────────────────┘
         ↓         ↓         ↓         ↓         ↓         ↓
┌──────────┐ ┌────────┐ ┌──────┐ ┌─────────┐ ┌──────┐ ┌─────┐
│Deep Learn │ │Symbolic│ │Graph│ │Associat.│ │Det. │ │ LLM │
└──────────┘ └────────┘ └──────┘ └─────────┘ └──────┘ └─────┘
```

### Flujo de Procesamiento

1. **Análisis de Tarea**: El motor analiza la tarea y selecciona paradigmas óptimos
2. **Ejecución Priorizada**: Ejecuta paradigmas en orden de prioridad
3. **Validación Cruzada**: Cada resultado es validado por otros paradigmas
4. **Corrección Anti-Alucinaciones**: LLM validado contra lógica, memoria y hechos
5. **Resultado Determinista**: Siempre que sea posible, usar resultados deterministas
6. **Confianza Calculada**: Confianza basada en validaciones cruzadas

## Características Clave

### Sin Alucinaciones
- **Validación Múltiple**: Cada salida LLM es validada por múltiples paradigmas
- **Corrección Automática**: Alucinaciones detectadas son corregidas automáticamente
- **Prioridad Determinista**: Algoritmos deterministas tienen máxima prioridad
- **Verdad Garantizada**: Solo se aceptan resultados validados lógicamente

### Determinismo
- **Reproducibilidad**: Algoritmos clásicos garantizan resultados reproducibles
- **Sin Aleatoriedad**: No se usa aleatoriedad en algoritmos críticos
- **Predecibilidad**: Comportamiento predecible en tareas deterministas
- **Cálculo Exacto**: Operaciones matemáticas exactas sin aproximaciones

### Memoria Asociativa
- **Recuerdo por Similitud**: Recuperación basada en similitud vectorial
- **Hopfield Networks**: Memoria auto-organizada con recuperación de patrones
- **Memoria Bidireccional**: Asociación bidireccional entre patrones
- **Contenido Direccionable**: Búsqueda rápida por contenido semántico

### Razonamiento Simbólico
- **Lógica Formal**: Razonamiento basado en lógica matemática
- **Sistemas Expertos**: Bases de conocimiento con reglas explícitas
- **Inferencia**: Encadenamiento hacia adelante y atrás
- **Resolución**: Algoritmo de resolución para demostración de teoremas

### Deep Learning
- **Redes Neuronales**: Implementación desde cero de redes neuronales
- **Backpropagation**: Entrenamiento con gradiente descendente
- **Reconocimiento**: Clasificación y reconocimiento de patrones
- **Aprendizaje**: Capacidad de aprender de datos (cuando sea necesario)

## API Django REST Framework

### Endpoints Neuro-Simbólicos

**Prefijo**: `/api/neuro-symbolic/`

- `POST /neuro-symbolic/process` - Procesa tarea neuro-simbólica
- `GET /neuro-symbolic/status` - Estado del sistema neuro-simbólico
- `POST /neuro-symbolic/knowledge` - Agregar conocimiento de dominio
- `POST /neuro-symbolic/validate` - Validar salida LLM contra alucinaciones

### Ejemplos de Uso

**Procesar tarea neuro-simbólica**:
```bash
curl -X POST http://localhost:8000/api/neuro-symbolic/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "calcular ruta óptima",
    "input_data": {
      "graph": {"A": {"B": 5, "C": 10}, "B": {"D": 3}, "C": {"D": 2}},
      "start": "A",
      "end": "D",
      "algorithm": "dijkstra"
    }
  }'
```

**Validar salida LLM**:
```bash
curl -X POST http://localhost:8000/api/neuro-symbolic/validate \
  -H "Content-Type: application/json" \
  -d '{
    "output": "La probabilidad de éxito es 150%",
    "context": "análisis de riesgo"
  }'
```

**Agregar conocimiento de dominio**:
```bash
curl -X POST http://localhost:8000/api/neuro-symbolic/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "facts": ["La probabilidad está entre 0 y 1", "La temperatura absoluta no puede ser negativa"],
    "patterns": [
      {
        "vector": [0.1, 0.2, 0.3, ...],
        "label": "probabilidad_valida",
        "metadata": {"domain": "matemáticas"}
      }
    ]
  }'
```

## Ventajas de la Arquitectura

### 1. Fiabilidad
- **Determinismo**: Resultados reproducibles en tareas críticas
- **Validación**: Múltiples capas de validación
- **Anti-alucinaciones**: Detección y corrección automática

### 2. Flexibilidad
- **Paradigmas Múltiples**: Selecciona el paradigma óptimo para cada tarea
- **Prioridades Configurables**: Ajuste de prioridades según dominio
- **Híbrido**: Combinación de fortalezas de cada paradigma

### 3. Verdad
- **Lógica Simbólica**: Garantía de consistencia lógica
- **Validación Factual**: Contradicción con hechos conocidos
- **Grafos de Conocimiento**: Validación contra ontología

### 4. Memoria
- **Memoria Asociativa**: Recuperación por similitud semántica
- **Redes de Hopfield**: Memoria auto-organizada
- **Qdrant**: Memoria vectorial para búsqueda semántica

### 5. Aprendizaje
- **Deep Learning**: Capacidad de aprender cuando es necesario
- **LLM Validado**: Generación de texto con validación
- **Sistemas Expertos**: Conocimiento explícito y reglas

## Comparación con Arquitecturas Tradicionales

| Característica | Arquitectura Tradicional | Arquitectura Neuro-Simbólica |
|---|---|---|
| **Alucinaciones** | Comunes en LLM | Detectadas y corregidas |
| **Determinismo** | Variable | Garantizado en algoritmos críticos |
| **Validación** | Limitada | Múltiple paradigmas |
| **Memoria** | Solo vectorial | Asociativa + vectorial |
| **Razonamiento** | Solo LLM | Simbólico + LLM |
| **Confiabilidad** | Baja en LLM | Alta por validación |
| **Explicabilidad** | Caja negra LLM | Explicable por lógica simbólica |

## Estado Actual

- ✅ **Neuronas Artificiales**: Implementado con redes neuronales desde cero
- ✅ **IA Simbólica**: Implementado con lógica formal y sistemas expertos
- ✅ **Memoria Asociativa**: Implementado con Hopfield, BAM y direccionable
- ✅ **Algoritmos Deterministas**: Implementados con búsqueda, ordenamiento, optimización
- ✅ **LLM**: Integrado con Ollama y validación anti-alucinaciones
- ✅ **Grafos**: Integrado con Neo4j y validación Cypher Gate
- ✅ **Anti-Alucinaciones**: Sistema completo de validación y corrección
- ✅ **Integración Híbrida**: Motor neuro-simbólico unificado
- ✅ **API Django**: Endpoints REST Framework para todos los paradigmas

## Próximos Pasos

1. **Testing**: Crear tests para cada paradigma
2. **Optimización**: Optimizar rendimiento de redes neuronales
3. **Expansión**: Agregar más algoritmos deterministas
4. **Grafos**: Expandir ontología del dominio
5. **LLM**: Evaluar modelos más grandes cuando el hardware lo permita
6. **Documentación**: Expandir documentación de API

## Conclusión

AutoPlan ahora es un sistema cognitivo neuro-simbólico que combina lo mejor de la IA clásica y moderna:

- **IA Clásica**: Lógica simbólica, algoritmos deterministas, sistemas expertos
- **IA Moderna**: Deep Learning, LLM, embeddings, grafos
- **Memoria**: Asociativa + vectorial para recuperación semántica
- **Verdad**: Anti-alucinaciones para garantizar veracidad
- **Determinismo**: Garantía de reproducibilidad donde sea crítico

Todo en una arquitectura unificada, local y soberana, sin dependencias de APIs externas.
