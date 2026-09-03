// ==========================================
// ESQUEMA DEL GRAFO TEOLOGICO-ESTRATEGICO
// Sistema Neo4j para Cognitive Core AGI
// ==========================================

// ==========================================
// 1. LIMPIEZA DE ESQUEMA EXISTENTE
// ==========================================
MATCH (n) DETACH DELETE n;

// ==========================================
// 2. CREACIÓN DE ÍNDICES PARA OPTIMIZACIÓN
// ==========================================
CREATE INDEX doctrine_name IF NOT EXISTS FOR (d:Doctrina) ON (d.name);
CREATE INDEX objection_name IF NOT EXISTS FOR (o:Objecion) ON (o.name);
CREATE INDEX spiritual_state_name IF NOT EXISTS FOR (s:Estado_Espiritual) ON (s.name);
CREATE INDEX conversion_strategy_name IF NOT EXISTS FOR (c:Estrategia_Conversion) ON (c.name);

// ==========================================
// 3. DEFINICIÓN DE CONSTRAINTS
// ==========================================
CREATE CONSTRAINT argument_id_unique IF NOT EXISTS FOR (a:Argumento) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT profile_id_unique IF NOT EXISTS FOR (p:Perfil) REQUIRE p.id IS UNIQUE;

// ==========================================
// 4. NODOS CORE DEL DOMINIO TEOLOGICO
// ==========================================

// Doctrinas fundamentales
CREATE (d1:Doctrina {
    name: "Trinidad",
    category: "Teologia_Proper",
    complexity: "high",
    strategic_importance: 0.95,
    biblical_basis: ["Mateo 28:19", "2 Corintios 13:14"],
    common_objections: [" politeísmo", "contradicción lógica"]
});

CREATE (d2:Doctrina {
    name: "Deidad_De_Cristo",
    category: "Cristologia",
    complexity: "high", 
    strategic_importance: 0.98,
    biblical_basis: ["Juan 1:1", "Colosenses 2:9"],
    common_objections: ["creación", "subordinación"]
});

CREATE (d3:Doctrina {
    name: "Justificacion_Por_Fe",
    category: "Soteriologia",
    complexity: "medium",
    strategic_importance: 0.92,
    biblical_basis: ["Romanos 3:28", "Gálatas 2:16"],
    common_objections: ["obras", "gracia barata"]
});

CREATE (d4:Doctrina {
    name: "Autoridad_De_La_Escritura",
    category: "Bibliologia",
    complexity: "medium",
    strategic_importance: 0.90,
    biblical_basis: ["2 Timoteo 3:16", "2 Pedro 1:20"],
    common_objections: ["contradicciones", "evolución cultural"]
});

// Objeciones comunes
CREATE (o1:Objecion {
    name: "Problema_Del_Mal",
    category: "Teodicea",
    frequency: "high",
    difficulty: "high",
    standard_refutations: ["libre_albedrío", "causa_mayor"]
});

CREATE (o2:Objecion {
    name: "Exclusivismo_Cristiano",
    category: "Misionologia",
    frequency: "medium",
    difficulty: "medium",
    standard_refutations: ["unicidad_de_Cristo", "revelación_general"]
});

CREATE (o3:Objecion {
    name: "Incompatibilidad_Ciencia_Fe",
    category: "Apologetica",
    frequency: "high",
    difficulty: "medium",
    standard_refutations: ["fe_y_razon", "diseño_inteligente"]
});

// Estados espirituales del perfil
CREATE (s1:Estado_Espiritual {
    name: "Ateo_Convencido",
    receptivity: 0.2,
    barriers: ["materialismo", "hostilidad_religiosa"],
    engagement_strategy: "intelectual",
    conversion_probability: 0.15
});

CREATE (s2:Estado_Espiritual {
    name: "Agnostico_Buscador",
    receptivity: 0.6,
    barriers: ["escepticismo", "falta_de_experiencia"],
    engagement_strategy: "experiencial",
    conversion_probability: 0.45
});

CREATE (s3:Estado_Espiritual {
    name: "Nominal_Cultural",
    receptivity: 0.4,
    barriers: ["apatía", "compromiso"],
    engagement_strategy: "relacional",
    conversion_probability: 0.35
});

CREATE (s4:Estado_Espiritual {
    name: "Creyente_Nominal",
    receptivity: 0.7,
    barriers: ["hipocresía", "falta_de_discipulado"],
    engagement_strategy: "discipulado",
    conversion_probability: 0.65
});

CREATE (s5:Estado_Espiritual {
    name: "Interesado_Espiritual",
    receptivity: 0.8,
    barriers: ["confusión", "miedo_al_compromiso"],
    engagement_strategy: "guiado",
    conversion_probability: 0.75
});

// Estrategias de conversión
CREATE (e1:Estrategia_Conversion {
    name: "Enfoque_Intelectual",
    type: "apologetica",
    effectiveness_profile: ["ateo_convenido", "agnostico"],
    time_commitment: "high",
    required_knowledge: ["filosofia", "ciencia", "historia"]
});

CREATE (e2:Estrategia_Conversion {
    name: "Enfoque_Experiencial",
    type: "testimonial",
    effectiveness_profile: ["agnostico_buscador", "interesado"],
    time_commitment: "medium",
    required_knowledge: ["experiencia_personal", "emocional"]
});

CREATE (e3:Estrategia_Conversion {
    name: "Enfoque_Relacional",
    type: "comunidad",
    effectiveness_profile: ["nominal_cultural", "creyente_nominal"],
    time_commitment: "high",
    required_knowledge: ["dinamica_grupal", "mentoría"]
});

CREATE (e4:Estrategia_Conversion {
    name: "Enfoque_Narrativo",
    type: "storytelling",
    effectiveness_profile: ["interesado", "nominal"],
    time_commitment: "medium",
    required_knowledge: ["biblia", "historia_biblica"]
});

// ==========================================
// 5. RELACIONES DEL DOMINIO TEOLOGICO
// ==========================================

// Doctrinas refutan objeciones
MATCH (d:Doctrina), (o:Objecion)
WHERE d.name IN (["Trinidad", "Deidad_De_Cristo"]) AND o.name = "Problema_Del_Mal"
CREATE (d)-[r1:REFUTA {
    strength: 0.8,
    approach: "teologico_sistemático",
    biblical_support: true
}]->(o);

MATCH (d:Doctrina), (o:Objecion)
WHERE d.name = "Deidad_De_Cristo" AND o.name = "Exclusivismo_Cristiano"
CREATE (d)-[r2:REFUTA {
    strength: 0.9,
    approach: "cristologico",
    biblical_support: true
}]->(o);

MATCH (d:Doctrina), (o:Objecion)
WHERE d.name = "Autoridad_De_La_Escritura" AND o.name = "Incompatibilidad_Ciencia_Fe"
CREATE (d)-[r3:REFUTA {
    strength: 0.7,
    approach: "epistemologico",
    biblical_support: true
}]->(o);

// Doctrinas soportan otras doctrinas
MATCH (d1:Doctrina), (d2:Doctrina)
WHERE d1.name = "Trinidad" AND d2.name = "Deidad_De_Cristo"
CREATE (d1)-[r4:SOPORTA {
    type: "fundamental",
    strength: 0.95
}]->(d2);

MATCH (d1:Doctrina), (d2:Doctrina)
WHERE d1.name = "Deidad_De_Cristo" AND d2.name = "Justificacion_Por_Fe"
CREATE (d1)-[r5:SOPORTA {
    type: "soteriologico",
    strength: 0.85
}]->(d2);

// Estados espirituales requieren estrategias específicas
MATCH (s:Estado_Espiritual), (e:Estrategia_Conversion)
WHERE s.name = "Ateo_Convencido" AND e.name = "Enfoque_Intelectual"
CREATE (s)-[r6:REQUIERE_ESTRATEGIA {
    effectiveness: 0.75,
    priority: "high"
}]->(e);

MATCH (s:Estado_Espiritual), (e:Estrategia_Conversion)
WHERE s.name = "Agnostico_Buscador" AND e.name = "Enfoque_Experiencial"
CREATE (s)-[r7:REQUIERE_ESTRATEGIA {
    effectiveness: 0.85,
    priority: "high"
}]->(e);

MATCH (s:Estado_Espiritual), (e:Estrategia_Conversion)
WHERE s.name = "Nominal_Cultural" AND e.name = "Enfoque_Relacional"
CREATE (s)-[r8:REQUIERE_ESTRATEGIA {
    effectiveness: 0.80,
    priority: "medium"
}]->(e);

// Estrategias conducen a conversión
MATCH (e:Estrategia_Conversion), (d:Doctrina)
WHERE e.name = "Enfoque_Intelectual" AND d.name = "Deidad_De_Cristo"
CREATE (e)-[r9:CONDUCE_A {
    doctrinal_focus: true,
    conversion_path: "intelectual"
}]->(d);

MATCH (e:Estrategia_Conversion), (d:Doctrina)
WHERE e.name = "Enfoque_Experiencial" AND d.name = "Justificacion_Por_Fe"
CREATE (e)-[r10:CONDUCE_A {
    doctrinal_focus: true,
    conversion_path: "experiencial"
}]->(d);

// ==========================================
// 6. NODOS DE PERFIL Y ARGUMENTOS
// ==========================================

// Perfiles de interacción
CREATE (p1:Perfil {
    id: "perfil_intelectual",
    name: "Perfil_Intelectual",
    characteristics: ["analítico", "escéptico", "preguntador"],
    preferred_argumentation: "logica",
    time_horizon: "largo_plazo"
});

CREATE (p2:Perfil {
    id: "perfil_emocional",
    name: "Perfil_Emocional",
    characteristics: ["sensible", "experiencial", "relacional"],
    preferred_argumentation: "testimonial",
    time_horizon: "corto_plazo"
});

CREATE (p3:Perfil {
    id: "perfil_pragmatico",
    name: "Perfil_Pragmatico",
    characteristics: ["práctico", "orientado_a_resultados", "directo"],
    preferred_argumentation: "consecuencial",
    time_horizon: "medio_plazo"
});

// Argumentos teológicos estructurados
CREATE (a1:Argumento {
    id: "arg_trinidad_logica",
    title: "Coherencia_Logica_Trinidad",
    type: "apologetico",
    complexity: "high",
    effectiveness_vs_atheist: 0.7,
    biblical_foundation: true
});

CREATE (a2:Argumento {
    id: "arg_cristo_historico",
    title: "Resurreccion_Historica",
    type: "historico",
    complexity: "medium",
    effectiveness_vs_atheist: 0.8,
    biblical_foundation: true
});

CREATE (a3:Argumento {
    id: "arg_justificacion_gracia",
    title: "Gracia_Versus_Obras",
    type: "soteriologico",
    complexity: "medium",
    effectiveness_vs_nominal: 0.85,
    biblical_foundation: true
});

// Relaciones de perfiles y argumentos
MATCH (p:Perfil), (a:Argumento)
WHERE p.id = "perfil_intelectual" AND a.id = "arg_trinidad_logica"
CREATE (p)-[r11:UTILIZA {
    effectiveness: 0.85,
    context: "debate_intelectual"
}]->(a);

MATCH (p:Perfil), (a:Argumento)
WHERE p.id = "perfil_emocional" AND a.id = "arg_cristo_historico"
CREATE (p)-[r12:UTILIZA {
    effectiveness: 0.90,
    context: "testimonio_personal"
}]->(a);

MATCH (p:Perfil), (a:Argumento)
WHERE p.id = "perfil_pragmatico" AND a.id = "arg_justificacion_gracia"
CREATE (p)-[r13:UTILIZA {
    effectiveness: 0.80,
    context: "vida_cotidiana"
}]->(a);

// Perfiles tienen estados espirituales
MATCH (p:Perfil), (s:Estado_Espiritual)
WHERE p.id = "perfil_intelectual" AND s.name = "Ateo_Convencido"
CREATE (p)-[r14:TIENE_ESTADO {
    probability: 0.6,
    transition_path: "agnosticismo"
}]->(s);

MATCH (p:Perfil), (s:Estado_Espiritual)
WHERE p.id = "perfil_emocional" AND s.name = "Agnostico_Buscador"
CREATE (p)-[r15:TIENE_ESTADO {
    probability: 0.7,
    transition_path: "interesado"
}]->(s);

// ==========================================
// 7. CONSULTAS DE UTILIDAD PARA EL SISTEMA
// ==========================================

// Encontrar la mejor estrategia para un estado espiritual
// MATCH (s:Estado_Espiritual {name: "Ateo_Convencido"})-[:REQUIERE_ESTRATEGIA]->(e:Estrategia_Conversion)
// RETURN e.name, e.type, e.effectiveness_profile;

// Encontrar objeciones que una doctrina puede refutar
// MATCH (d:Doctrina {name: "Trinidad"})-[:REFUTA]->(o:Objecion)
// RETURN o.name, o.category, o.difficulty;

// Encontrar argumentos efectivos para un perfil
// MATCH (p:Perfil {id: "perfil_intelectual"})-[:UTILIZA]->(a:Argumento)
// RETURN a.title, a.type, a.effectiveness_vs_atheist;

// ==========================================
// 8. ESTATÍSTICAS DEL ESQUEMA
// ==========================================

// Verificar creación del esquema
MATCH (n) 
RETURN labels(n) as node_labels, count(n) as count
ORDER BY count DESC;