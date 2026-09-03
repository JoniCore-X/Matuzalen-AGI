"""
Motor de Razonamiento - Núcleo de Procesamiento Cognitivo
Implementa razonamiento basado en conocimiento y memoria
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime

class ReasoningEngine:
    def __init__(self, cognitive_memory, knowledge_graph):
        self.cognitive_memory = cognitive_memory
        self.knowledge_graph = knowledge_graph
        self.initialized = False

    async def initialize(self):
        """Inicializa el motor de razonamiento"""
        self.initialized = True
        print("[REASONING ENGINE] Initialized successfully")

    async def analyze_intention(self, intention: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la intención y extrae información clave"""
        try:
            # Análisis básico de la intención
            keywords = self._extract_keywords(intention)
            action_type = self._classify_action_type(intention)
            complexity = self._assess_complexity(intention, context)
            
            return {
                "keywords": keywords,
                "action_type": action_type,
                "complexity": complexity,
                "context_summary": self._summarize_context(context)
            }
        except Exception as e:
            print(f"[REASONING ENGINE] Error analyzing intention: {e}")
            return {"keywords": [], "action_type": "unknown", "complexity": "medium"}

    async def generate_decision(
        self,
        intention: str,
        context: Dict[str, Any],
        relevant_knowledge: List[Dict],
        graph_relations: List[Dict],
        urgency: str
    ) -> Dict[str, Any]:
        """Genera una decisión basada en conocimiento y razonamiento"""
        try:
            # Paso 1: Evaluar el conocimiento relevante
            knowledge_weight = self._evaluate_knowledge_relevance(relevant_knowledge)
            
            # Paso 2: Analizar relaciones del grafo
            relation_insights = self._analyze_graph_relations(graph_relations)
            
            # Paso 3: Determinar nivel de riesgo
            risk_level = self._assess_risk_level(intention, context, urgency)
            
            # Paso 4: Generar acción sugerida
            suggested_action = self._generate_suggested_action(
                intention,
                context,
                relevant_knowledge,
                relation_insights,
                risk_level
            )
            
            # Paso 5: Calcular confianza
            confidence = self._calculate_confidence(
                knowledge_weight,
                relation_insights,
                risk_level,
                urgency
            )
            
            # Paso 6: Determinar si requiere aprobación humana
            requires_approval = self._determine_approval_need(risk_level, confidence, urgency)
            
            # Paso 7: Generar razonamiento explicativo
            reasoning = self._generate_reasoning(
                intention,
                suggested_action,
                knowledge_weight,
                relation_insights,
                risk_level,
                confidence
            )
            
            # Paso 8: Extraer conceptos relacionados
            related_concepts = self._extract_related_concepts(relevant_knowledge, graph_relations)
            
            return {
                "action": suggested_action,
                "reasoning": reasoning,
                "confidence": confidence,
                "requires_approval": requires_approval,
                "risk_level": risk_level,
                "related_concepts": related_concepts
            }
            
        except Exception as e:
            print(f"[REASONING ENGINE] Error generating decision: {e}")
            # Fallback a decisión básica
            return self._generate_fallback_decision(intention, urgency)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave del texto"""
        # Palabras comunes a ignorar
        stop_words = {"el", "la", "de", "en", "y", "a", "que", "por", "con", "un", "una", "para", "es", "son"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        return keywords[:10]  # Top 10 keywords

    def _classify_action_type(self, intention: str) -> str:
        """Clasifica el tipo de acción de la intención"""
        intention_lower = intention.lower()
        
        action_patterns = {
            "analysis": ["analizar", "examinar", "evaluar", "estudiar", "investigar"],
            "creation": ["crear", "generar", "desarrollar", "construir", "diseñar"],
            "modification": ["modificar", "cambiar", "actualizar", "editar", "ajustar"],
            "deletion": ["eliminar", "borrar", "remover", "destruir"],
            "execution": ["ejecutar", "correr", "iniciar", "lanzar", "procesar"],
            "communication": ["enviar", "comunicar", "notificar", "informar"],
            "decision": ["decidir", "elegir", "seleccionar", "determinar"]
        }
        
        for action_type, patterns in action_patterns.items():
            if any(pattern in intention_lower for pattern in patterns):
                return action_type
        
        return "general"

    def _assess_complexity(self, intention: str, context: Dict[str, Any]) -> str:
        """Evalúa la complejidad de la tarea"""
        complexity_score = 0
        
        # Longitud de la intención
        if len(intention) > 100:
            complexity_score += 1
        if len(intention) > 200:
            complexity_score += 1
        
        # Complejidad del contexto
        if len(context) > 5:
            complexity_score += 1
        if len(context) > 10:
            complexity_score += 1
        
        # Palabras complejas
        complex_words = ["integrar", "orquestar", "optimizar", "coordinar", "sincronizar"]
        if any(word in intention.lower() for word in complex_words):
            complexity_score += 1
        
        if complexity_score >= 3:
            return "high"
        elif complexity_score >= 1:
            return "medium"
        else:
            return "low"

    def _summarize_context(self, context: Dict[str, Any]) -> str:
        """Genera un resumen del contexto"""
        if not context:
            return "No context provided"
        
        keys = list(context.keys())[:5]
        return f"Context with {len(context)} keys: {', '.join(keys)}"

    def _evaluate_knowledge_relevance(self, knowledge: List[Dict]) -> float:
        """Evalúa la relevancia del conocimiento disponible"""
        if not knowledge:
            return 0.0
        
        # Calcular score promedio de similitud
        total_score = sum(k.get("score", 0) for k in knowledge)
        avg_score = total_score / len(knowledge) if knowledge else 0
        
        return min(avg_score, 1.0)

    def _analyze_graph_relations(self, relations: List[Dict]) -> Dict[str, Any]:
        """Analiza las relaciones del grafo para insights"""
        if not relations:
            return {"has_relations": False, "insights": []}
        
        # Contar tipos de relaciones
        relation_types = {}
        for rel in relations:
            rel_type = rel.get("relation_type", "unknown")
            relation_types[rel_type] = relation_types.get(rel_type, 0) + 1
        
        # Generar insights
        insights = []
        for rel_type, count in relation_types.items():
            if count > 2:
                insights.append(f"Strong {rel_type} patterns detected ({count} occurrences)")
        
        return {
            "has_relations": True,
            "relation_count": len(relations),
            "relation_types": relation_types,
            "insights": insights
        }

    def _assess_risk_level(self, intention: str, context: Dict[str, Any], urgency: str) -> str:
        """Evalúa el nivel de riesgo de la acción"""
        risk_score = 0
        
        # Palabras de alto riesgo
        high_risk_words = ["eliminar", "borrar", "destruir", "formatear", "reiniciar"]
        if any(word in intention.lower() for word in high_risk_words):
            risk_score += 2
        
        # Urgencia alta aumenta riesgo
        if urgency == "high":
            risk_score += 1
        
        # Contexto con datos sensibles
        sensitive_keys = ["password", "token", "secret", "key", "credential"]
        if any(key in context for key in sensitive_keys):
            risk_score += 2
        
        if risk_score >= 3:
            return "high"
        elif risk_score >= 1:
            return "medium"
        else:
            return "low"

    def _generate_suggested_action(
        self,
        intention: str,
        context: Dict[str, Any],
        knowledge: List[Dict],
        relations: Dict[str, Any],
        risk_level: str
    ) -> str:
        """Genera una acción sugerida basada en el análisis"""
        action_type = self._classify_action_type(intention)
        
        # Si hay conocimiento relevante, usarlo para refinar la acción
        if knowledge and knowledge[0].get("score", 0) > 0.7:
            base_action = f"Execute {action_type} based on similar past patterns"
        else:
            base_action = f"Execute {action_type} with standard procedures"
        
        # Añadir contexto de riesgo
        if risk_level == "high":
            base_action += " with enhanced safety measures"
        elif risk_level == "medium":
            base_action += " with standard safety checks"
        
        return base_action

    def _calculate_confidence(
        self,
        knowledge_weight: float,
        relations: Dict[str, Any],
        risk_level: str,
        urgency: str
    ) -> float:
        """Calcula el nivel de confianza en la decisión"""
        confidence = 0.5  # Base confidence
        
        # Aumentar confianza basado en conocimiento
        confidence += knowledge_weight * 0.3
        
        # Aumentar confianza si hay relaciones relevantes
        if relations.get("has_relations", False):
            confidence += 0.1
        
        # Reducir confianza basado en riesgo
        if risk_level == "high":
            confidence *= 0.7
        elif risk_level == "medium":
            confidence *= 0.85
        
        # Ajustar por urgencia
        if urgency == "high":
            confidence *= 0.9  # Menos confianza en decisiones rápidas
        
        return min(max(confidence, 0.0), 1.0)

    def _determine_approval_need(self, risk_level: str, confidence: float, urgency: str) -> bool:
        """Determina si la decisión requiere aprobación humana"""
        # Requiere aprobación si riesgo alto
        if risk_level == "high":
            return True
        
        # Requiere aprobación si confianza baja
        if confidence < 0.7:
            return True
        
        # Requiere aprobación si urgencia alta con confianza media
        if urgency == "high" and confidence < 0.85:
            return True
        
        return False

    def _generate_reasoning(
        self,
        intention: str,
        action: str,
        knowledge_weight: float,
        relations: Dict[str, Any],
        risk_level: str,
        confidence: float
    ) -> str:
        """Genera un razonamiento explicativo"""
        reasoning_parts = [
            f"Analyzed intention: '{intention}'",
            f"Selected action: {action}",
            f"Knowledge relevance: {(knowledge_weight * 100):.1f}%",
            f"Risk level: {risk_level}",
            f"Confidence: {(confidence * 100):.1f}%"
        ]
        
        if relations.get("has_relations", False):
            reasoning_parts.append(f"Graph relations: {relations['relation_count']} patterns found")
        
        return " | ".join(reasoning_parts)

    def _extract_related_concepts(self, knowledge: List[Dict], relations: List[Dict]) -> List[str]:
        """Extrae conceptos relacionados del conocimiento y relaciones"""
        concepts = []
        
        # Extraer del conocimiento
        for k in knowledge[:3]:
            content = k.get("content", "")
            words = content.split()
            concepts.extend([w for w in words if len(w) > 4 and w[0].isupper()][:2])
        
        # Extraer de las relaciones
        for rel in relations[:5]:
            concepts.append(rel.get("entity", ""))
            concepts.append(rel.get("related_entity", ""))
        
        # Eliminar duplicados y limitar
        return list(set(concepts))[:8]

    def _generate_fallback_decision(self, intention: str, urgency: str) -> Dict[str, Any]:
        """Genera una decisión de fallback cuando hay errores"""
        return {
            "action": f"Standard execution for: {intention}",
            "reasoning": "Fallback decision due to processing errors - using standard procedures",
            "confidence": 0.5,
            "requires_approval": urgency == "high",
            "risk_level": "high" if urgency == "high" else "medium",
            "related_concepts": []
        }

    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrae entidades del texto (versión simplificada)"""
        # En producción, usar NLP avanzado (spaCy, NLTK, etc.)
        words = text.split()
        entities = []
        
        for i, word in enumerate(words):
            # Palabras que parecen entidades (capitalizadas, >3 caracteres)
            if len(word) > 3 and word[0].isupper():
                entities.append({
                    "name": word,
                    "type": "unknown",
                    "confidence": 0.7,
                    "position": i
                })
        
        return entities[:10]  # Limitar a 10 entidades

    def is_healthy(self) -> bool:
        """Verifica si el motor está saludable"""
        return self.initialized