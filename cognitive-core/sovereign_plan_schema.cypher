// Matuzalen AGI - Esquema de Persistencia de la Voluntad
// Grafo de Ejecucion con Event Sourcing para Planes Estrategicos y Teologicos

// ---------------------------------------------------------
// I. NODOS PRINCIPALES
// ---------------------------------------------------------

//(:Usuario) - Identidad soberana
CREATE CONSTRAINT usuario_id IF NOT EXISTS
FOR (u:Usuario) REQUIRE u.id IS UNIQUE;

//(:Plan) - Estrategia temporal y semantica viva
CREATE CONSTRAINT plan_id IF NOT EXISTS
FOR (p:Plan) REQUIRE p.id IS UNIQUE;

//(:Objetivo) - Meta del plan
CREATE CONSTRAINT objetivo_id IF NOT EXISTS
FOR (o:Objetivo) REQUIRE o.id IS UNIQUE;

//(:Fase) - Etapa del plan
CREATE CONSTRAINT fase_id IF NOT EXISTS
FOR (f:Fase) REQUIRE f.id IS UNIQUE;

//(:Accion) - Paso ejecutable
CREATE CONSTRAINT accion_id IF NOT EXISTS
FOR (a:Accion) REQUIRE a.id IS UNIQUE;

//(:Recurso) - Recurso necesario
CREATE CONSTRAINT recurso_id IF NOT EXISTS
FOR (r:Recurso) REQUIRE r.id IS UNIQUE;

//(:Riesgo) - Riesgo detectado
CREATE CONSTRAINT riesgo_id IF NOT EXISTS
FOR (r:Riesgo) REQUIRE r.id IS UNIQUE;

//(:Evento) - Event sourcing: cada cambio es un evento inmutable
CREATE CONSTRAINT evento_id IF NOT EXISTS
FOR (e:Evento) REQUIRE e.id IS UNIQUE;

// ---------------------------------------------------------
// II. INDICES PARA BUSQUEDA SEMANTICA Y TEMPORAL
// ---------------------------------------------------------

CREATE INDEX plan_user_id IF NOT EXISTS
FOR (p:Plan) ON (p.user_id);

CREATE INDEX plan_activo IF NOT EXISTS
FOR (p:Plan) ON (p.activo);

CREATE INDEX fase_plan_id IF NOT EXISTS
FOR (f:Fase) ON (f.plan_id);

CREATE INDEX accion_fase_id IF NOT EXISTS
FOR (a:Accion) ON (a.fase_id);

CREATE INDEX evento_plan_id IF NOT EXISTS
FOR (e:Evento) ON (e.plan_id);

CREATE INDEX evento_timestamp IF NOT EXISTS
FOR (e:Evento) ON (e.timestamp);

// ---------------------------------------------------------
// III. EJEMPLO DE CREACION DE UN PLAN ESTRATEGICO
// ---------------------------------------------------------

// Crear usuario soberano
CREATE (u:Usuario {
  id: 'user-001',
  identity_node: 'Usuario:Arquitecto',
  spiritual_profile: 'Estratega_Dominante',
  clearance_level: 'Omega',
  created_at: datetime()
});

// Crear plan activo
CREATE (p:Plan {
  id: 'plan-001',
  user_id: 'user-001',
  nombre: 'Expansion de la Red de Influencia',
  proposito: 'Establecer dominio estrategico digital',
  estado: 'activo',
  activo: true,
  created_at: datetime(),
  updated_at: datetime()
});

// Relacionar usuario con plan
MATCH (u:Usuario {id: 'user-001'}), (p:Plan {id: 'plan-001'})
CREATE (u)-[:POSEE {desde: datetime()}]->(p);

// Crear objetivo principal
CREATE (o:Objetivo {
  id: 'obj-001',
  plan_id: 'plan-001',
  descripcion: 'Captar 10,000 nuevos contactos cualificados',
  criterio_exito: 'Base de datos con 10k registros verificados',
  prioridad: 1.0
});

MATCH (p:Plan {id: 'plan-001'}), (o:Objetivo {id: 'obj-001'})
CREATE (p)-[:TIENE_OBJETIVO {peso: 1.0}]->(o);

// Crear fases
CREATE (f1:Fase {id: 'fase-001', plan_id: 'plan-001', nombre: 'Ingestion de Datos', orden: 1, estado: 'en_progreso'});
CREATE (f2:Fase {id: 'fase-002', plan_id: 'plan-001', nombre: 'Segmentacion', orden: 2, estado: 'pendiente'});
CREATE (f3:Fase {id: 'fase-003', plan_id: 'plan-001', nombre: 'Conversion', orden: 3, estado: 'pendiente'});

MATCH (p:Plan {id: 'plan-001'})
MATCH (f1:Fase {id: 'fase-001'}), (f2:Fase {id: 'fase-002'}), (f3:Fase {id: 'fase-003'})
CREATE (p)-[:CONTIENE_FASE {orden: 1}]->(f1)
CREATE (p)-[:CONTIENE_FASE {orden: 2}]->(f2)
CREATE (p)-[:CONTIENE_FASE {orden: 3}]->(f3)
CREATE (f1)-[:SIGUE_A]->(f2)
CREATE (f2)-[:SIGUE_A]->(f3);

// Crear acciones
CREATE (a1:Accion {id: 'acc-001', fase_id: 'fase-001', descripcion: 'Desplegar scrapers en fuentes objetivo', estado: 'pendiente', prioridad: 0.9});
CREATE (a2:Accion {id: 'acc-002', fase_id: 'fase-001', descripcion: 'Normalizar datos y eliminar duplicados', estado: 'pendiente', prioridad: 0.8});

MATCH (f1:Fase {id: 'fase-001'})
MATCH (a1:Accion {id: 'acc-001'}), (a2:Accion {id: 'acc-002'})
CREATE (f1)-[:INCLUYE_ACCION {orden: 1}]->(a1)
CREATE (f1)-[:INCLUYE_ACCION {orden: 2}]->(a2)
CREATE (a1)-[:PRECEDE_A]->(a2);

// Crear recursos
CREATE (r1:Recurso {id: 'rec-001', plan_id: 'plan-001', nombre: 'API de Twitter/X', tipo: 'api', disponibilidad: 'limitada'});
CREATE (r2:Recurso {id: 'rec-002', plan_id: 'plan-001', nombre: 'Cluster de scraping', tipo: 'infraestructura', disponibilidad: 'alta'});

MATCH (a1:Accion {id: 'acc-001'}), (r1:Recurso {id: 'rec-001'}), (r2:Recurso {id: 'rec-002'})
CREATE (a1)-[:REQUIERE {cantidad: 1, critico: true}]->(r1)
CREATE (a1)-[:REQUIERE {cantidad: 1, critico: true}]->(r2);

// Crear riesgos
CREATE (ri1:Riesgo {id: 'riesgo-001', plan_id: 'plan-001', descripcion: 'Rate-limiting de API de Twitter/X', probabilidad: 0.8, impacto: 0.9});

MATCH (a1:Accion {id: 'acc-001'}), (ri1:Riesgo {id: 'riesgo-001'})
CREATE (a1)-[:BLOQUEA {severidad: 0.85}]->(ri1);

// ---------------------------------------------------------
// IV. EVENT SOURCING - Cada cambio es un evento inmutable
// ---------------------------------------------------------

// Ejemplo de evento: PLAN_CREADO
CREATE (e1:Evento {
  id: 'evt-001',
  plan_id: 'plan-001',
  tipo: 'PLAN_CREADO',
  actor: 'user-001',
  timestamp: datetime(),
  payload: '{"plan_id": "plan-001", "nombre": "Expansion de la Red de Influencia"}'
});

MATCH (p:Plan {id: 'plan-001'}), (e1:Evento {id: 'evt-001'})
CREATE (p)-[:TIENE_EVENTO]->(e1);

// Ejemplo de evento: ACCION_MODIFICADA
CREATE (e2:Evento {
  id: 'evt-002',
  plan_id: 'plan-001',
  tipo: 'ACCION_MODIFICADA',
  actor: 'AGI',
  timestamp: datetime(),
  payload: '{"accion_id": "acc-001", "cambio": "estado", "valor_anterior": "pendiente", "valor_nuevo": "en_progreso"}'
});

MATCH (p:Plan {id: 'plan-001'}), (e2:Evento {id: 'evt-002'})
CREATE (p)-[:TIENE_EVENTO]->(e2);

// Evento de refutacion por el AGI
CREATE (e3:Evento {
  id: 'evt-003',
  plan_id: 'plan-001',
  tipo: 'ACCION_REFUTADA_POR_CORTEX',
  actor: 'AGI',
  timestamp: datetime(),
  payload: '{"accion_id": "acc-001", "razon": "Riesgo de rate-limiting supera umbral aceptable", "nueva_ruta": "acc-004"}'
});

MATCH (p:Plan {id: 'plan-001'}), (e3:Evento {id: 'evt-003'})
CREATE (p)-[:TIENE_EVENTO]->(e3);

// Relacion de refutacion entre acciones
MATCH (a1:Accion {id: 'acc-001'}), (ri1:Riesgo {id: 'riesgo-001'})
CREATE (ri1)-[:REFUTA_A {razon: 'Rate-limiting inminente'}]->(a1);

// ---------------------------------------------------------
// V. CONSULTAS DE NAVEGACION PARA EL AGI
// ---------------------------------------------------------

// Obtener plan activo con fases, acciones, recursos y riesgos
MATCH (u:Usuario {id: 'user-001'})-[:POSEE]->(p:Plan {activo: true})
OPTIONAL MATCH (p)-[:CONTIENE_FASE]->(f:Fase)
OPTIONAL MATCH (f)-[:INCLUYE_ACCION]->(a:Accion)
OPTIONAL MATCH (a)-[:REQUIERE]->(r:Recurso)
OPTIONAL MATCH (a)-[:BLOQUEA]->(ri:Riesgo)
OPTIONAL MATCH (ri)-[:REFUTA_A]->(a)
RETURN p, collect(DISTINCT f) AS fases, collect(DISTINCT a) AS acciones,
       collect(DISTINCT r) AS recursos, collect(DISTINCT ri) AS riesgos
ORDER BY f.orden, a.prioridad DESC;

// Obtener historia de eventos de un plan (event sourcing)
MATCH (p:Plan {id: 'plan-001'})-[:TIENE_EVENTO]->(e:Evento)
RETURN e.tipo, e.actor, e.timestamp, e.payload
ORDER BY e.timestamp DESC;

// Detectar cuellos de botella criticos
MATCH (a:Accion)-[:BLOQUEA]->(r:Riesgo)
WHERE r.probabilidad > 0.7 AND r.impacto > 0.7
RETURN a.descripcion AS accion, r.descripcion AS riesgo,
       r.probabilidad * r.impacto AS severidad
ORDER BY severidad DESC;

// Proximos pasos logicos segun el grafo
MATCH (p:Plan {id: 'plan-001'})-[:CONTIENE_FASE]->(f:Fase {estado: 'en_progreso'})
MATCH (f)-[:INCLUYE_ACCION]->(a:Accion {estado: 'pendiente'})
OPTIONAL MATCH (a)-[:PRECEDE_A]->(sig:Accion)
RETURN a.id AS accion_id, a.descripcion AS siguiente_accion,
       collect(sig.descripcion) AS acciones_siguientes
ORDER BY a.prioridad DESC
LIMIT 3;
