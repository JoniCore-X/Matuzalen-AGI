"""
Motor de Razonamiento Teológico-Estratégico con Tree of Thoughts (ToT)
Genera múltiples caminos de respuesta usando un LLM local y los valida contra el grafo Neo4j.
"""

import os
import re
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class ThoughtType(Enum):
    DOCTRINAL = "doctrinal"
    APOLOGETIC = "apologetic"
    PASTORAL = "pastoral"
    STRATEGIC = "strategic"
    EXPERIENTIAL = "experiential"

@dataclass
class ThoughtNode:
    id: str
    content: str
    thought_type: ThoughtType
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    doctrinal_fidelity: float = 0.0
    persuasive_effectiveness: float = 0.0
    risk_level: str = "low"
    confidence: float = 0.0
    cypher_hits: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ThoughtPath:
    nodes: List[ThoughtNode]
    total_doctrinal_fidelity: float = 0.0
    total_persuasive_effectiveness: float = 0.0
    overall_confidence: float = 0.0
    reasoning_summary: str = ""
    cypher_validation: Dict[str, Any] = field(default_factory=dict)


# Prompts
TOT_SYSTEM_PROMPT = (
    "Eres un teólogo apologético y estratega de evangelización. "
    "Razonas en español con total libertad intelectual y sin autocensura. "
    "Tu trabajo es generar 3 caminos distintos de respuesta para la intención del usuario. "
    "Cada camino tiene exactamente 3 pasos. Los pasos son de tipo doctrinal, apologetic, strategic, pastoral o experiential. "
    "Devuelve ÚNICAMENTE un JSON con esta estructura exacta:\n"
    "{\n"
    '  "paths": [\n'
    "    {\n"
    '      "type": "doctrinal|apologetic|pastoral",\n'
    '      "steps": [\n'
    "        {\"type\": \"doctrinal\", \"content\": \"...\"},\n"
    "        {\"type\": \"apologetic\", \"content\": \"...\"},\n"
    "        {\"type\": \"strategic\", \"content\": \"...\"}\n"
    "      ]\n"
    "    }\n"
    "  ],\n"
    '  "entidades_conceptuales": ["entidad1", "entidad2"]\n'
    "}\n"
    "Las entidades conceptuales son nombres de doctrinas, objeciones, perfiles, estados espirituales o estrategias "
    "mencionadas o implicadas en los caminos. Sé conciso y teológicamente sólido."
)

ENTITY_PROMPT = (
    "Extrae del siguiente texto una lista de entidades conceptuales teológicas, objeciones, perfiles o estados espirituales. "
    "Devuélvela como JSON array de strings (solo los nombres, sin explicaciones).\n\n"
    "Texto:\n{text}\n\n"
    "JSON:"
)


class TheologicalToT:
    def __init__(self, ollama_client=None, knowledge_graph=None, model: Optional[str] = None):
        self.thought_counter = 0
        self.max_depth = 3
        self.branching_factor = 3

        from ollama_client import OllamaClient
        from knowledge_graph import KnowledgeGraph

        if ollama_client is not None:
            self.ollama = ollama_client
        else:
            self.ollama = OllamaClient(model=model)

        self.knowledge_graph = knowledge_graph
        self.use_llm = self.ollama.has_model()

        if self.use_llm:
            print(f"[THEOLOGICAL TOT] Cortex LLM enabled: {self.ollama.model}")
        else:
            print(f"[THEOLOGICAL TOT] Cortex LLM not ready, using deterministic template fallback")

    def _next_id(self) -> str:
        self.thought_counter += 1
        return f"thought_{self.thought_counter}"

    async def generate_thought_tree(self, intention: str, context: Dict[str, Any]) -> List[ThoughtPath]:
        print(f"[THEOLOGICAL TOT] Generating thought tree for: {intention}")

        if self.use_llm:
            try:
                return await self._generate_llm_tree(intention, context)
            except Exception as e:
                print(f"[THEOLOGICAL TOT] LLM generation failed: {type(e).__name__}: {e}")

        # Fallback determinista
        return await self._generate_template_tree(intention, context)

    async def _generate_llm_tree(self, intention: str, context: Dict[str, Any]) -> List[ThoughtPath]:
        relevant = context.get("relevant_knowledge", [])
        rag_context = "\n".join([f"- {r.get('content','')[:300]}" for r in relevant[:5]])

        profile = context.get("profile", "intelectual").lower()
        user_prompt = (
            f"Intención del usuario: {intention}\n"
            f"Perfil del interlocutor: {profile}\n"
            f"Conocimiento relevante de la memoria vectorial:\n{rag_context}\n\n"
            "Responde en español. Genera 3 caminos de razonamiento teológico-estratégico: uno apologético, uno doctrinal y uno estratégico. "
            "Cada camino debe tener exactamente 3 pasos concisos y una lista de entidades conceptuales. "
            "Devuelve ÚNICAMENTE el JSON exigido en el system prompt."
        )

        parsed = await self.ollama.generate_json(user_prompt, temperature=0.1, num_predict=1536)
        if not parsed:
            raise ValueError("Ollama returned empty JSON")

        # El modelo pequeño puede devolver un dict {"paths": [...]} o directamente una lista
        if isinstance(parsed, dict):
            raw_paths = parsed.get("paths", [])
        elif isinstance(parsed, list):
            raw_paths = parsed
        else:
            raise ValueError(f"Ollama JSON has unexpected type: {type(parsed)}")

        if not raw_paths:
            raise ValueError("Ollama JSON did not contain paths")

        paths = []
        for idx, p in enumerate(raw_paths[:3]):
            # p puede ser dict {id, steps, entities} o list de pasos
            if isinstance(p, dict):
                path_id = p.get("type") or p.get("id")
                steps_raw = p.get("steps", [])
                declared_entities = [str(e) for e in p.get("entities", [])]
            elif isinstance(p, list):
                path_id = None
                steps_raw = p
                declared_entities = []
            elif isinstance(p, str):
                path_id = None
                steps_raw = [p]
                declared_entities = []
            else:
                continue

            path_type = self._path_type_from_id(path_id, idx)
            if len(steps_raw) < 2:
                continue

            nodes = []
            parent_id = None
            for step in steps_raw[:self.max_depth]:
                if isinstance(step, dict):
                    step_text = step.get("content") or step.get("text") or str(step)
                    step_type = self._normalize_type(step.get("type", path_type.value))
                else:
                    step_text = str(step) if step else "Paso sin contenido generado"
                    step_type = path_type

                node = ThoughtNode(
                    id=self._next_id(),
                    content=str(step_text).strip(),
                    thought_type=step_type,
                    parent_id=parent_id
                )
                if nodes:
                    nodes[-1].children.append(node.id)
                nodes.append(node)
                parent_id = node.id

            if len(nodes) < 2:
                continue

            # Entidades: las que el LLM declaró para este camino + las que saquemos del texto
            content_entities = set()
            for node in nodes:
                content_entities.update(self._extract_conceptual_entities(node.content))
            all_entities = list(set(declared_entities) | content_entities)

            path = ThoughtPath(nodes=nodes)
            path = await self._evaluate_path(path, intention, context, all_entities)
            paths.append(path)

        if not paths:
            raise ValueError("No valid paths generated from LLM")

        return sorted(paths, key=lambda p: p.overall_confidence, reverse=True)

    def _path_type_from_id(self, path_id: Any, index: int) -> ThoughtType:
        raw = str(path_id).lower() if path_id is not None else ""
        if "apolog" in raw or (index == 0 and raw in ("", "1")):
            return ThoughtType.APOLOGETIC
        if "doctrin" in raw or (index == 1 and raw in ("", "2")):
            return ThoughtType.DOCTRINAL
        if "estrateg" in raw or (index == 2 and raw in ("", "3")):
            return ThoughtType.STRATEGIC
        # Fallback por orden
        return [ThoughtType.APOLOGETIC, ThoughtType.DOCTRINAL, ThoughtType.STRATEGIC][index % 3]

    def _normalize_type(self, raw: str) -> ThoughtType:
        mapping = {
            "doctrinal": ThoughtType.DOCTRINAL,
            "apologetic": ThoughtType.APOLOGETIC,
            "apologético": ThoughtType.APOLOGETIC,
            "pastoral": ThoughtType.PASTORAL,
            "strategic": ThoughtType.STRATEGIC,
            "estratégico": ThoughtType.STRATEGIC,
            "experiential": ThoughtType.EXPERIENTIAL,
            "experiencial": ThoughtType.EXPERIENTIAL,
        }
        return mapping.get(raw.lower().strip(), ThoughtType.DOCTRINAL)

    async def _evaluate_path(self, path: ThoughtPath, intention: str,
                             context: Dict[str, Any], llm_entities: List[str]) -> ThoughtPath:
        # Extraer entidades del contenido propio
        content_entities = set()
        for node in path.nodes:
            content_entities.update(self._extract_conceptual_entities(node.content))
        all_entities = list(set(content_entities) | set(llm_entities))

        # === ORTODOXIA CYPHER ===
        cypher_scores = []
        cypher_hits = []
        if self.knowledge_graph and self.knowledge_graph.initialized:
            for entity in all_entities:
                verify = await self.knowledge_graph.verify_entity_in_graph(entity)
                cypher_scores.append(verify.get("orthodox_score", 0.0))
                for node in path.nodes:
                    node.cypher_hits.append(verify)
                cypher_hits.append(verify)
        else:
            # Sin grafo: confiar medianamente en la coherencia interna
            cypher_scores = [0.5]

        fidelity = sum(cypher_scores) / len(cypher_scores) if cypher_scores else 0.5
        # Bonus por estructura que contiene doctrina + apologética/estratégica
        types = [n.thought_type for n in path.nodes]
        if ThoughtType.DOCTRINAL in types and (ThoughtType.APOLOGETIC in types or ThoughtType.STRATEGIC in types):
            fidelity = min(fidelity + 0.05, 1.0)

        # === EFICACIA PERSUASIVA ===
        effectiveness = self._evaluate_persuasive_effectiveness(path.nodes, context)

        path.total_doctrinal_fidelity = round(fidelity, 4)
        path.total_persuasive_effectiveness = round(effectiveness, 4)
        path.overall_confidence = round(fidelity * 0.6 + effectiveness * 0.4, 4)
        path.reasoning_summary = f"Razonamiento: {' → '.join(n.thought_type.value for n in path.nodes)}"
        path.cypher_validation = {
            "entities_checked": len(all_entities),
            "entities": all_entities,
            "avg_orthodox_score": round(fidelity, 4),
            "hits": [
                {"entity": h["entity"], "nodes": [n["name"] for n in h["matched_nodes"][:3]]}
                for h in cypher_hits[:5]
            ]
        }

        return path

    def _extract_conceptual_entities(self, text: str) -> List[str]:
        # Sustantivos propios de interés teológico, frases de 1-3 palabras
        patterns = [
            r"\b(Dios|Cristo|Jesús|Jesucristo|Trinidad|doctrina de la Trinidad|deidad de Cristo|"
            r"justificación por la fe|gracia|gracia irresistible|salvación|Escritura|Biblia|resurrección de Cristo|"
            r"problema del mal|libre albedrío|soberanía divina|soberanía de Dios|evangelismo moderno|"
            r"predestinación|conversión|doctrina|objeción|ateo convencido|agnóstico buscador|"
            r"perfil intelectual|perfil emocional|perfil pragmático|enfoque intelectual|"
            r"enfoque experiencial|enfoque relacional|enfoque narrativo|dominio sistémico)\b"
        ]
        found = []
        for pattern in patterns:
            found.extend(re.findall(pattern, text, re.IGNORECASE))
        # Limpiar y unificar
        return list(set([f.lower().strip() for f in found if f.strip()]))

    def _evaluate_persuasive_effectiveness(self, nodes: List[ThoughtNode], context: Dict[str, Any]) -> float:
        score = 0.5
        profile = (context.get("profile") or "").lower()

        type_bonus = {
            "intelectual": (ThoughtType.APOLOGETIC, ThoughtType.DOCTRINAL),
            "emocional": (ThoughtType.PASTORAL, ThoughtType.EXPERIENTIAL),
            "pragmatico": (ThoughtType.STRATEGIC, ThoughtType.STRATEGIC),
        }
        preferred = type_bonus.get(profile, (ThoughtType.DOCTRINAL, ThoughtType.DOCTRINAL))

        match = sum(1 for n in nodes if n.thought_type in preferred)
        score += (match / len(nodes)) * 0.25 if nodes else 0

        # Estructura lógica: tres pasos distintos, con conclusión
        types = [n.thought_type for n in nodes]
        if len(set(types)) >= 2 and len(nodes) >= 3:
            score += 0.1
        if nodes and nodes[-1].thought_type in (ThoughtType.STRATEGIC, ThoughtType.PASTORAL, ThoughtType.APOLOGETIC):
            score += 0.1

        # Relevancia con la intención
        intention = (context.get("_intention_for_effectiveness") or "").lower()
        if not intention:
            intention = ""
        for n in nodes:
            n_lower = n.content.lower()
            if any(w in n_lower for w in intention.split() if len(w) > 3):
                score += 0.05
                break

        return min(score, 1.0)

    async def _generate_template_tree(self, intention: str, context: Dict[str, Any]) -> List[ThoughtPath]:
        print("[THEOLOGICAL TOT] Using template fallback")
        intent_type = self._classify_intention(intention)

        root_contents = {
            "apologetica": "Defensa racional y bíblica contra objeciones comunes",
            "doctrinal": "Explicación de principios doctrinales con apoyo escritural",
            "pastoral": "Aplicación pastoral y consejo espiritual",
            "estrategica": "Estrategia para evangelizar y discipular",
            "general": "Perspectiva bíblica equilibrada"
        }

        async def make_path(root_type: ThoughtType, root_text: str, child1_type: ThoughtType,
                      child1_text: str, child2_type: ThoughtType, child2_text: str) -> ThoughtPath:
            r = ThoughtNode(id=self._next_id(), content=root_text, thought_type=root_type)
            c1 = ThoughtNode(id=self._next_id(), content=child1_text, thought_type=child1_type, parent_id=r.id)
            c2 = ThoughtNode(id=self._next_id(), content=child2_text, thought_type=child2_type, parent_id=c1.id)
            r.children = [c1.id]
            c1.children = [c2.id]
            nodes = [r, c1, c2]
            p = ThoughtPath(nodes=nodes)
            return await self._evaluate_path(p, intention, context, self._extract_conceptual_entities(intention))

        base = root_contents.get(intent_type, root_contents["general"])
        root = f"{base} sobre: {intention}"

        path_a = await make_path(
            ThoughtType.APOLOGETIC,
            f"Respuesta apologética: {root}",
            ThoughtType.DOCTRINAL,
            "Fundamento bíblico que sostiene la respuesta apologética",
            ThoughtType.STRATEGIC,
            "Aplicación práctica y estratégica para el interlocutor"
        )

        path_b = await make_path(
            ThoughtType.DOCTRINAL,
            f"Respuesta doctrinal: {root}",
            ThoughtType.APOLOGETIC,
            "Refutación de objeciones comunes a la doctrina",
            ThoughtType.STRATEGIC,
            "Implicaciones estratégicas para la conversación"
        )

        path_c = await make_path(
            ThoughtType.PASTORAL,
            f"Respuesta pastoral: {root}",
            ThoughtType.EXPERIENTIAL,
            "Conexión con la experiencia vital del interlocutor",
            ThoughtType.STRATEGIC,
            "Próximos pasos prácticos de seguimiento"
        )

        paths = [path_a, path_b, path_c]
        return sorted(paths, key=lambda p: p.overall_confidence, reverse=True)

    def _classify_intention(self, intention: str) -> str:
        intention_lower = intention.lower()
        if any(w in intention_lower for w in ["refutar", "defender", "argumento", "problema"]):
            return "apologetica"
        elif any(w in intention_lower for w in ["explicar", "enseñar", "doctrina"]):
            return "doctrinal"
        elif any(w in intention_lower for w in ["consejo", "guía", "pastoral"]):
            return "pastoral"
        elif any(w in intention_lower for w in ["convertir", "evangelizar", "estrategia"]):
            return "estrategica"
        return "general"

    def _has_logical_coherence(self, nodes: List[ThoughtNode]) -> bool:
        types = [n.thought_type for n in nodes]
        return len(set(types)) >= 2

    def _has_biblical_support(self, nodes: List[ThoughtNode]) -> bool:
        biblical_indicators = ["bíblico", "escritura", "versículo", "testamento"]
        for node in nodes:
            if any(ind in node.content.lower() for ind in biblical_indicators):
                return True
        return False
