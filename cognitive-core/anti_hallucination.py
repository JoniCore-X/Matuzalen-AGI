"""
Sistema Anti-Alucinaciones
Valida y corrige alucinaciones usando lógica simbólica, memoria asociativa y algoritmos deterministas.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime


class HallucinationType(Enum):
    """Tipos de alucinaciones detectadas"""
    FACTUAL = "factual"  # Contradice hechos conocidos
    LOGICAL = "logical"  # Contradice lógica formal
    TEMPORAL = "temporal"  # Inconsistencia temporal
    NUMERICAL = "numerical"  # Error en datos numéricos
    CONSISTENCY = "consistency"  # Inconsistencia interna
    DOMAIN = "domain"  # Fuera del dominio de conocimiento


@dataclass
class HallucinationDetection:
    """Detección de alucinación"""
    type: HallucinationType
    severity: float  # 0.0 a 1.0
    confidence: float
    location: str  # dónde se detectó
    original_text: str
    corrected_text: Optional[str] = None
    evidence: List[str] = None


@dataclass
class ValidationReport:
    """Reporte de validación de contenido"""
    is_hallucination: bool
    confidence_score: float
    detections: List[HallucinationDetection]
    corrected_content: Optional[str] = None
    validation_method: str = "hybrid"


class AntiHallucinationSystem:
    """Sistema anti-alucinaciones neuro-simbólico"""

    def __init__(self):
        from symbolic_ai import SymbolicReasoner
        from associative_memory import AssociativeMemoryEngine
        from deterministic_algorithms import DeterministicAlgorithmEngine

        self.symbolic_reasoner = SymbolicReasoner()
        self.associative_memory = AssociativeMemoryEngine()
        self.deterministic_engine = DeterministicAlgorithmEngine()

        self.knowledge_base: Dict[str, Any] = {}
        self.validation_history: List[ValidationReport] = []

    def add_knowledge(self, fact: str, certainty: float = 1.0) -> None:
        """Agrega conocimiento factual al sistema"""
        try:
            expression = self.symbolic_reasoner.parse_expression(fact)
            self.symbolic_reasoner.add_fact(expression, certainty=certainty)
            self.knowledge_base[fact] = certainty
        except:
            # Si no es una expresión lógica, guardar como texto
            self.knowledge_base[fact] = certainty

    def validate_factual_claim(self, claim: str) -> HallucinationDetection:
        """Valida una afirmación factual contra la base de conocimiento"""
        # Verificar si la afirmación contradice hechos conocidos
        contradictions = []

        for fact, certainty in self.knowledge_base.items():
            if self._contradicts(claim, fact):
                contradictions.append((fact, certainty))

        if contradictions:
            # Encontramos contradicciones
            strongest_contradiction = max(contradictions, key=lambda x: x[1])
            return HallucinationDetection(
                type=HallucinationType.FACTUAL,
                severity=strongest_contradiction[1],
                confidence=0.8,
                location="factual_validation",
                original_text=claim,
                evidence=[c[0] for c in contradictions]
            )

        return HallucinationDetection(
            type=HallucinationType.FACTUAL,
            severity=0.0,
            confidence=0.0,
            location="factual_validation",
            original_text=claim
        )

    def validate_logical_consistency(self, statements: List[str]) -> List[HallucinationDetection]:
        """Valida consistencia lógica entre múltiples afirmaciones"""
        detections = []

        try:
            # Parsear todas las afirmaciones
            expressions = [self.symbolic_reasoner.parse_expression(s) for s in statements]

            # Verificar contradicciones lógicas
            for i, expr1 in enumerate(expressions):
                for j, expr2 in enumerate(expressions[i+1:], i+1):
                    if self.symbolic_reasoner.check_contradiction(expr1):
                        detections.append(HallucinationDetection(
                            type=HallucinationType.LOGICAL,
                            severity=0.7,
                            confidence=0.6,
                            location=f"statement_{i}_vs_{j}",
                            original_text=statements[i],
                            evidence=[statements[j]]
                        ))

        except Exception as e:
            # Si no se pueden parsear, usar validación de texto
            for i, stmt1 in enumerate(statements):
                for j, stmt2 in enumerate(statements[i+1:], i+1):
                    if self._text_contradicts(stmt1, stmt2):
                        detections.append(HallucinationDetection(
                            type=HallucinationType.LOGICAL,
                            severity=0.5,
                            confidence=0.4,
                            location=f"statement_{i}_vs_{j}",
                            original_text=stmt1,
                            evidence=[stmt2]
                        ))

        return detections

    def validate_numerical_data(self, text: str) -> List[HallucinationDetection]:
        """Valida datos numéricos en el texto"""
        detections = []
        numbers = self._extract_numbers(text)

        for num, context in numbers:
            # Validaciones numéricas deterministas
            if self._is_impossible_number(num, context):
                detections.append(HallucinationDetection(
                    type=HallucinationType.NUMERICAL,
                    severity=0.8,
                    confidence=0.7,
                    location="numerical_validation",
                    original_text=context,
                    corrected_text=self._correct_number(num, context)
                ))

        return detections

    def validate_with_memory(self, text: str) -> HallucinationDetection:
        """Valida usando memoria asociativa"""
        # Convertir texto a vector (simplificado)
        vector = self._text_to_vector(text)

        # Buscar en memoria asociativa
        similar_patterns = self.associative_memory.retrieve_pattern(vector, k=3)

        if similar_patterns:
            # Si hay patrones muy similares, verificar consistencia
            max_similarity = similar_patterns[0].get('similarity', 0)

            if max_similarity > 0.9:
                # Posible duplicado o consistencia
                return HallucinationDetection(
                    type=HallucinationType.CONSISTENCY,
                    severity=0.3,
                    confidence=0.6,
                    location="memory_validation",
                    original_text=text,
                    evidence=[p['label'] for p in similar_patterns]
                )

        return HallucinationDetection(
            type=HallucinationType.CONSISTENCY,
            severity=0.0,
            confidence=0.0,
            location="memory_validation",
            original_text=text
        )

    def validate_llm_output(self, llm_output: str, context: str = "") -> ValidationReport:
        """Validación completa de salida de LLM"""
        detections = []

        # 1. Validación factual
        factual_detection = self.validate_factual_claim(llm_output)
        if factual_detection.severity > 0.3:
            detections.append(factual_detection)

        # 2. Validación lógica
        statements = self._extract_statements(llm_output)
        if len(statements) > 1:
            logical_detections = self.validate_logical_consistency(statements)
            detections.extend(logical_detections)

        # 3. Validación numérica
        numerical_detections = self.validate_numerical_data(llm_output)
        detections.extend(numerical_detections)

        # 4. Validación con memoria
        memory_detection = self.validate_with_memory(llm_output)
        if memory_detection.severity > 0.3:
            detections.append(memory_detection)

        # Calcular puntuación de confianza
        if detections:
            max_severity = max(d.severity for d in detections)
            avg_confidence = sum(d.confidence for d in detections) / len(detections)
            confidence_score = 1.0 - (max_severity * avg_confidence)
        else:
            confidence_score = 1.0

        # Corregir contenido si hay alucinaciones
        corrected_content = None
        if detections:
            corrected_content = self._correct_hallucinations(llm_output, detections)

        report = ValidationReport(
            is_hallucination=len(detections) > 0,
            confidence_score=confidence_score,
            detections=detections,
            corrected_content=corrected_content,
            validation_method="neuro_symbolic_hybrid"
        )

        self.validation_history.append(report)
        return report

    def _contradicts(self, claim: str, fact: str) -> bool:
        """Verifica si una afirmación contradice un hecho"""
        # Simplificación: comparación de texto
        claim_lower = claim.lower()
        fact_lower = fact.lower()

        # Palabras negativas
        negations = ["no", "not", "nunca", "jamás", "falso", "incorrecto", "imposible"]

        # Si el hecho tiene negación y la afirmación no, o viceversa
        has_negation_claim = any(neg in claim_lower for neg in negations)
        has_negation_fact = any(neg in fact_lower for neg in negations)

        if has_negation_claim != has_negation_fact:
            # Verificar si comparten palabras clave
            claim_words = set(claim_lower.split())
            fact_words = set(fact_lower.split())
            common_words = claim_words & fact_words

            if len(common_words) > 2:  # Suficiente superposición
                return True

        return False

    def _text_contradicts(self, text1: str, text2: str) -> bool:
        """Verifica contradicción simple entre textos"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Palabras opuestas
        opposites = {
            "siempre": ["nunca", "jamás"],
            "verdadero": ["falso", "incorrecto"],
            "mayor": ["menor"],
            "aumenta": ["disminuye", "reduce"],
            "positivo": ["negativo"]
        }

        for word, opposites_list in opposites.items():
            if word in words1:
                if any(op in words2 for op in opposites_list):
                    return True

        return False

    def _extract_numbers(self, text: str) -> List[Tuple[float, str]]:
        """Extrae números del texto con contexto"""
        import re
        numbers = []

        # Encontrar números con contexto
        matches = re.finditer(r'[-+]?\d*\.\d+|\d+', text)
        for match in matches:
            num = float(match.group())
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end]
            numbers.append((num, context))

        return numbers

    def _is_impossible_number(self, num: float, context: str) -> bool:
        """Verifica si un número es imposible en el contexto"""
        # Validaciones deterministas
        if "edad" in context.lower():
            return num < 0 or num > 150
        if "porcentaje" in context.lower():
            return num < 0 or num > 100
        if "probabilidad" in context.lower():
            return num < 0 or num > 1
        if "temperatura" in context.lower():
            if "celsius" in context.lower():
                return num < -273.15 or num > 1000
            if "kelvin" in context.lower():
                return num < 0

        return False

    def _correct_number(self, num: float, context: str) -> str:
        """Corrige un número imposible"""
        if "edad" in context.lower():
            return str(max(0, min(150, int(num))))
        if "porcentaje" in context.lower():
            return str(max(0, min(100, int(num))))
        if "probabilidad" in context.lower():
            return str(max(0, min(1, num)))
        if "temperatura" in context.lower():
            if "celsius" in context.lower():
                return str(max(-273.15, min(1000, num)))
            if "kelvin" in context.lower():
                return str(max(0, num))

        return str(num)

    def _extract_statements(self, text: str) -> List[str]:
        """Extrae afirmaciones del texto"""
        # Simplificación: dividir por puntos
        statements = [s.strip() for s in text.split('.') if s.strip()]
        return statements

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Convierte texto a vector (simplificado)"""
        # Usar hash de palabras como vector
        words = text.lower().split()
        vector_size = 768
        vector = np.zeros(vector_size)

        for i, word in enumerate(words):
            hash_val = hash(word) % vector_size
            vector[hash_val] += 1

        # Normalizar
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def _correct_hallucinations(self, text: str, detections: List[HallucinationDetection]) -> str:
        """Corrige alucinaciones en el texto"""
        corrected = text

        for detection in detections:
            if detection.corrected_text:
                corrected = corrected.replace(detection.original_text, detection.corrected_text)

        return corrected

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de validación"""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "hallucination_rate": 0.0,
                "average_confidence": 0.0,
                "hallucination_types": {}
            }

        total = len(self.validation_history)
        hallucinations = sum(1 for r in self.validation_history if r.is_hallucination)
        avg_confidence = sum(r.confidence_score for r in self.validation_history) / total

        type_counts = {}
        for report in self.validation_history:
            for detection in report.detections:
                type_name = detection.type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "total_validations": total,
            "hallucination_rate": hallucinations / total,
            "average_confidence": avg_confidence,
            "hallucination_types": type_counts
        }


class HallucinationCorrector:
    """Corrector de alucinaciones usando múltiples paradigmas"""

    def __init__(self):
        self.anti_hallucination = AntiHallucinationSystem()

    def correct_llm_response(self, llm_response: str, context: str = "") -> Dict[str, Any]:
        """Corrige una respuesta de LLM"""
        validation_report = self.anti_hallucination.validate_llm_output(llm_response, context)

        result = {
            "original": llm_response,
            "corrected": validation_report.corrected_content or llm_response,
            "is_hallucination": validation_report.is_hallucination,
            "confidence": validation_report.confidence_score,
            "detections": [
                {
                    "type": d.type.value,
                    "severity": d.severity,
                    "location": d.location,
                    "evidence": d.evidence
                }
                for d in validation_report.detections
            ]
        }

        return result

    def add_domain_knowledge(self, domain_facts: List[str]) -> None:
        """Agrega conocimiento de dominio"""
        for fact in domain_facts:
            self.anti_hallucination.add_knowledge(fact, certainty=1.0)

    def validate_claim(self, claim: str) -> Dict[str, Any]:
        """Valida una afirmación específica"""
        detection = self.anti_hallucination.validate_factual_claim(claim)

        return {
            "claim": claim,
            "is_hallucination": detection.severity > 0.3,
            "severity": detection.severity,
            "confidence": detection.confidence,
            "evidence": detection.evidence
        }


# Instancias globales
anti_hallucination_system = AntiHallucinationSystem()
hallucination_corrector = HallucinationCorrector()
