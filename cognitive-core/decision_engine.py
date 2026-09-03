"""
Motor de Toma de Decisiones - Interfaz de Alto Nivel

Este motor ahora actúa como interfaz con el núcleo cognitivo AGI.
Desacoplado de la lógica de decisión local, delega al servicio cognitivo.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class Urgency(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class DecisionOption:
    """Opción de decisión"""
    action: str
    description: str
    risk_level: RiskLevel
    expected_outcome: str
    confidence: float


@dataclass
class DecisionContext:
    """Contexto de decisión"""
    situation: str
    data: Dict[str, Any]
    urgency: Urgency
    confidence: float
    alternatives: List[DecisionOption]


@dataclass
class Decision:
    """Decisión tomada"""
    selected_option: DecisionOption
    reasoning: str
    timestamp: datetime
    requires_human_approval: bool
    monitored: bool


class DecisionEngine:
    """Motor de toma de decisiones con integración cognitiva"""

    def __init__(self):
        self.decision_history: List[Decision] = []
        self.learning_patterns: Dict[str, float] = {}
        self.safety_threshold: float = 0.8
        self.cognitive_client = None
        try:
            from cognitive_client import CognitiveClient
            self.cognitive_client = CognitiveClient()
        except ImportError:
            print('[DECISION ENGINE] Cognitive client not available, using local decision making only')

    async def make_decision(self, context: DecisionContext) -> Decision:
        """Evalúa una situación y toma una decisión"""
        # Verificar urgencia y confianza
        if context.urgency == Urgency.HIGH and context.confidence < self.safety_threshold:
            return self._create_high_urgency_decision(context)

        # Intentar usar el núcleo cognitivo AGI
        if self.cognitive_client:
            try:
                from cognitive_client import CognitiveClient, CognitiveRequest, UrgencyLevel

                cognitive_response = await self.cognitive_client.process_intention(
                    CognitiveRequest(
                        intention=context.situation,
                        context=context.data,
                        urgency=UrgencyLevel(context.urgency.value),
                        metadata={
                            'alternatives': [
                                {
                                    'action': alt.action,
                                    'description': alt.description,
                                    'risk_level': alt.risk_level.value,
                                    'expected_outcome': alt.expected_outcome,
                                    'confidence': alt.confidence
                                }
                                for alt in context.alternatives
                            ],
                            'confidence': context.confidence
                        }
                    )
                )

                # Convertir respuesta cognitiva a decisión local
                selected_option = self._find_matching_option(
                    cognitive_response.decision,
                    context.alternatives
                )

                decision = Decision(
                    selected_option=selected_option or context.alternatives[0],
                    reasoning=cognitive_response.reasoning,
                    timestamp=datetime.now(),
                    requires_human_approval=cognitive_response.requires_human_approval,
                    monitored=True
                )

                self.decision_history.append(decision)
                self._learn_from_decision(decision, context)

                return decision
            except Exception as error:
                print(f'[DECISION ENGINE] Cognitive service unavailable, using local fallback: {error}')
                # Fallback a procesamiento local original
                return await self._make_local_decision(context)
        else:
            # Usar procesamiento local directamente
            return await self._make_local_decision(context)

    async def _make_local_decision(self, context: DecisionContext) -> Decision:
        """Procesamiento local de decisión (fallback)"""
        # Analizar opciones disponibles
        evaluated_options = await self._evaluate_options(context)

        # Seleccionar mejor opción
        selected_option = self._select_best_option(evaluated_options)

        # Generar razonamiento
        reasoning = self._generate_reasoning(selected_option, context)

        # Determinar si requiere aprobación humana
        requires_approval = self._determine_approval_need(selected_option, context)

        # Registrar decisión
        decision = Decision(
            selected_option=selected_option,
            reasoning=reasoning,
            timestamp=datetime.now(),
            requires_human_approval=requires_approval,
            monitored=True
        )

        self.decision_history.append(decision)
        self._learn_from_decision(decision, context)

        return decision

    def _find_matching_option(self, cognitive_decision: str, alternatives: List[DecisionOption]) -> Optional[DecisionOption]:
        """Encuentra la opción que mejor coincide con la decisión cognitiva"""
        # Búsqueda simple por coincidencia de texto
        for option in alternatives:
            if (cognitive_decision.lower() in option.action.lower() or
                option.action.lower() in cognitive_decision.lower()):
                return option
        return None

    async def _evaluate_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Evalúa cada opción disponible"""
        return [
            DecisionOption(
                action=option.action,
                description=option.description,
                risk_level=option.risk_level,
                expected_outcome=option.expected_outcome,
                confidence=self._calculate_option_confidence(option, context)
            )
            for option in context.alternatives
        ]

    def _calculate_option_confidence(self, option: DecisionOption, context: DecisionContext) -> float:
        """Calcula la confianza de una opción específica"""
        confidence = option.confidence

        # Ajustar por nivel de riesgo
        if option.risk_level == RiskLevel.HIGH:
            confidence *= 0.7
        elif option.risk_level == RiskLevel.MEDIUM:
            confidence *= 0.85

        # Ajustar por patrones aprendidos
        pattern_key = f"{context.situation}_{option.action}"
        pattern_confidence = self.learning_patterns.get(pattern_key, 0)
        confidence = (confidence + pattern_confidence) / 2

        return min(confidence, 1.0)

    def _select_best_option(self, options: List[DecisionOption]) -> DecisionOption:
        """Selecciona la mejor opción basándose en múltiples factores"""
        # Ordenar por confianza y nivel de riesgo
        risk_score = {RiskLevel.HIGH: 0, RiskLevel.MEDIUM: 0.5, RiskLevel.LOW: 1}

        sorted_options = sorted(
            options,
            key=lambda opt: (
                risk_score[opt.risk_level],
                opt.confidence
            ),
            reverse=True
        )

        return sorted_options[0]

    def _generate_reasoning(self, option: DecisionOption, context: DecisionContext) -> str:
        """Genera razonamiento explicativo"""
        factors = [
            f"Situación: {context.situation}",
            f"Urgencia: {context.urgency.value}",
            f"Acción seleccionada: {option.action}",
            f"Nivel de riesgo: {option.risk_level.value}",
            f"Confianza: {option.confidence * 100:.1f}%",
            f"Resultado esperado: {option.expected_outcome}"
        ]

        return ', '.join(factors)

    def _determine_approval_need(self, option: DecisionOption, context: DecisionContext) -> bool:
        """Determina si la decisión requiere aprobación humana"""
        # Requiere aprobación si:
        # - Nivel de riesgo alto
        # - Confianza baja
        # - Urgencia alta con baja confianza
        return (
            option.risk_level == RiskLevel.HIGH or
            option.confidence < self.safety_threshold or
            (context.urgency == Urgency.HIGH and option.confidence < 0.9)
        )

    def _create_high_urgency_decision(self, context: DecisionContext) -> Decision:
        """Manejo de situaciones de alta urgencia"""
        safest_options = [opt for opt in context.alternatives if opt.risk_level == RiskLevel.LOW]
        if safest_options:
            safest_option = max(safest_options, key=lambda opt: opt.confidence)
        else:
            safest_option = context.alternatives[0]

        return Decision(
            selected_option=safest_option,
            reasoning=f"High urgency situation - selected safest option with {safest_option.confidence * 100:.1f}% confidence",
            timestamp=datetime.now(),
            requires_human_approval=True,
            monitored=True
        )

    def _learn_from_decision(self, decision: Decision, context: DecisionContext) -> None:
        """Aprendizaje de decisiones pasadas"""
        pattern_key = f"{context.situation}_{decision.selected_option.action}"
        current_confidence = self.learning_patterns.get(pattern_key, 0)

        # Si la decisión fue exitosa (no requiere intervención humana), aumentar confianza
        if not decision.requires_human_approval:
            new_confidence = min(current_confidence + 0.1, 1.0)
            self.learning_patterns[pattern_key] = new_confidence

    def get_decision_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de decisiones"""
        total = len(self.decision_history)
        if total == 0:
            return {
                'total_decisions': 0,
                'human_approval_rate': 0,
                'average_confidence': 0,
                'risk_distribution': {}
            }

        approval_required = sum(1 for d in self.decision_history if d.requires_human_approval)
        avg_confidence = sum(d.selected_option.confidence for d in self.decision_history) / total

        risk_distribution = {}
        for decision in self.decision_history:
            risk = decision.selected_option.risk_level.value
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

        return {
            'total_decisions': total,
            'human_approval_rate': (approval_required / total) * 100,
            'average_confidence': avg_confidence,
            'risk_distribution': risk_distribution
        }

    def clear_history(self) -> None:
        """Limpiar historial de decisiones"""
        self.decision_history = []
        print('[DECISION ENGINE] Decision history cleared')


# Instancia del motor de decisiones
decision_engine = DecisionEngine()
