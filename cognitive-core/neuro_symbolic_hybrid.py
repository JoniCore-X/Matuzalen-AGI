"""
Arquitectura Neuro-Simbólica Híbrida
Integra todos los paradigmas de IA: Deep Learning, IA Simbólica, Memoria Asociativa,
Algoritmos Deterministas, LLM y Grafos en una arquitectura unificada sin alucinaciones.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime

# Importar todos los paradigmas
from neural_networks import DeepLearningEngine, NeuralNetworkConfig, NeuralLayer, LayerType, ActivationFunction
from symbolic_ai import SymbolicReasoner, ExpertSystem, LogicSolver
from associative_memory import AssociativeMemoryEngine, MemoryType
from deterministic_algorithms import DeterministicAlgorithmEngine, AlgorithmType
from anti_hallucination import AntiHallucinationSystem, HallucinationCorrector


class Paradigm(Enum):
    """Paradigmas de IA disponibles"""
    DEEP_LEARNING = "deep_learning"
    SYMBOLIC = "symbolic"
    ASSOCIATIVE_MEMORY = "associative_memory"
    DETERMINISTIC = "deterministic"
    LLM = "llm"
    GRAPH = "graph"
    HYBRID = "hybrid"


@dataclass
class CognitiveProcess:
    """Proceso cognitivo que usa múltiples paradigmas"""
    task: str
    paradigms_used: List[Paradigm]
    input_data: Any
    intermediate_results: Dict[str, Any]
    final_result: Any
    confidence: float
    validation_passed: bool
    execution_time: float


class NeuroSymbolicEngine:
    """Motor neuro-simbólico que integra todos los paradigmas"""

    def __init__(self):
        # Inicializar todos los motores de paradigmas
        self.deep_learning = DeepLearningEngine()
        self.symbolic_reasoner = SymbolicReasoner()
        self.associative_memory = AssociativeMemoryEngine()
        self.deterministic_engine = DeterministicAlgorithmEngine()
        self.anti_hallucination = AntiHallucinationSystem()
        self.hallucination_corrector = HallucinationCorrector()

        # Historial de procesos
        self.process_history: List[CognitiveProcess] = []

        # Configuración de prioridades de paradigmas
        self.paradigm_priorities = {
            Paradigm.SYMBOLIC: 0.9,  # Alta prioridad para lógica
            Paradigm.DETERMINISTIC: 0.95,  # Máxima prioridad para determinismo
            Paradigm.ASSOCIATIVE_MEMORY: 0.8,
            Paradigm.DEEP_LEARNING: 0.7,
            Paradigm.LLM: 0.6,  # Baja prioridad para LLM (validado)
            Paradigm.GRAPH: 0.85
        }

    def process_task(self, task: str, input_data: Any, paradigms: List[Paradigm] = None) -> CognitiveProcess:
        """Procesa una tarea cognitiva usando paradigmas específicos"""
        start_time = datetime.now()

        if paradigms is None:
            paradigms = self._select_optimal_paradigms(task)

        intermediate_results = {}
        final_result = None
        validation_passed = True
        confidence = 0.0

        # Ejecutar paradigmas en orden de prioridad
        sorted_paradigms = sorted(paradigms, key=lambda p: self.paradigm_priorities.get(p, 0.5), reverse=True)

        for paradigm in sorted_paradigms:
            try:
                result = self._execute_paradigm(paradigm, task, input_data, intermediate_results)
                intermediate_results[paradigm.value] = result

                # Validar resultado
                if self._validate_result(result, paradigm):
                    confidence += self.paradigm_priorities[paradigm]
                else:
                    validation_passed = False
                    print(f"[NEURO-SYMBOLIC] Validation failed for {paradigm.value}")

                # Si el paradigma es determinista y tiene resultado, usarlo
                if paradigm == Paradigm.DETERMINISTIC and result.success:
                    final_result = result.result
                    break

            except Exception as e:
                print(f"[NEURO-SYMBOLIC] Error in {paradigm.value}: {e}")
                continue

        # Si no hay resultado determinista, usar el último disponible
        if final_result is None and intermediate_results:
            last_paradigm = list(intermediate_results.keys())[-1]
            final_result = intermediate_results[last_paradigm]

        # Normalizar confianza
        confidence = min(confidence / len(paradigms), 1.0)

        execution_time = (datetime.now() - start_time).total_seconds()

        process = CognitiveProcess(
            task=task,
            paradigms_used=paradigms,
            input_data=input_data,
            intermediate_results=intermediate_results,
            final_result=final_result,
            confidence=confidence,
            validation_passed=validation_passed,
            execution_time=execution_time
        )

        self.process_history.append(process)
        return process

    def _select_optimal_paradigms(self, task: str) -> List[Paradigm]:
        """Selecciona los paradigmas óptimos para una tarea"""
        task_lower = task.lower()

        # Análisis de tarea para determinar paradigmas
        if any(word in task_lower for word in ["calcular", "ordenar", "buscar", "optimizar", "planificar"]):
            return [Paradigm.DETERMINISTIC, Paradigm.SYMBOLIC]

        if any(word in task_lower for word in ["reconocer", "clasificar", "patrón", "aprender"]):
            return [Paradigm.DEEP_LEARNING, Paradigm.ASSOCIATIVE_MEMORY]

        if any(word in task_lower for word in ["lógica", "razonar", "deducir", "probar"]):
            return [Paradigm.SYMBOLIC, Paradigm.DETERMINISTIC]

        if any(word in task_lower for word in ["recordar", "memorizar", "asociar", "recuperar"]):
            return [Paradigm.ASSOCIATIVE_MEMORY, Paradigm.DEEP_LEARNING]

        if any(word in task_lower for word in ["generar", "crear", "escribir", "explicar"]):
            return [Paradigm.LLM, Paradigm.SYMBOLIC, Paradigm.ASSOCIATIVE_MEMORY]

        # Por defecto, usar híbrido completo
        return [Paradigm.HYBRID]

    def _execute_paradigm(self, paradigm: Paradigm, task: str, input_data: Any,
                         context: Dict[str, Any]) -> Any:
        """Ejecuta un paradigma específico"""
        if paradigm == Paradigm.DEEP_LEARNING:
            return self._execute_deep_learning(task, input_data, context)

        elif paradigm == Paradigm.SYMBOLIC:
            return self._execute_symbolic(task, input_data, context)

        elif paradigm == Paradigm.ASSOCIATIVE_MEMORY:
            return self._execute_associative_memory(task, input_data, context)

        elif paradigm == Paradigm.DETERMINISTIC:
            return self._execute_deterministic(task, input_data, context)

        elif paradigm == Paradigm.LLM:
            return self._execute_llm(task, input_data, context)

        elif paradigm == Paradigm.GRAPH:
            return self._execute_graph(task, input_data, context)

        elif paradigm == Paradigm.HYBRID:
            return self._execute_hybrid(task, input_data, context)

        else:
            raise ValueError(f"Unknown paradigm: {paradigm}")

    def _execute_deep_learning(self, task: str, input_data: Any, context: Dict[str, Any]) -> Any:
        """Ejecuta paradigma de Deep Learning"""
        # Si no hay red creada, crear una por defecto
        if not self.deep_learning.active_networks:
            self.deep_learning.create_pattern_network(
                network_id="default",
                input_size=10,
                hidden_layers=[64, 32],
                output_size=5
            )

        # Convertir input_data a formato numpy si es necesario
        if isinstance(input_data, list):
            input_array = np.array(input_data)
        else:
            input_array = np.array([input_data] if isinstance(input_data, (int, float)) else [0])

        # Asegurar dimensiones correctas
        if len(input_array.shape) == 1:
            input_array = input_array.reshape(1, -1)

        # Ajustar tamaño si es necesario
        if input_array.shape[1] != 10:
            input_array = np.resize(input_array, (input_array.shape[0], 10))

        try:
            result = self.deep_learning.recognize_patterns("default", input_array)
            return {"success": True, "result": result, "paradigm": "deep_learning"}
        except:
            return {"success": False, "result": None, "paradigm": "deep_learning"}

    def _execute_symbolic(self, task: str, input_data: Any, context: Dict[str, Any]) -> Any:
        """Ejecuta paradigma simbólico"""
        if isinstance(input_data, str):
            # Parsear como expresión lógica
            try:
                expression = self.symbolic_reasoner.parse_expression(input_data)
                # Evaluar con asignación vacía
                result = self.symbolic_reasoner.evaluate_expression(expression, {})
                return {"success": True, "result": result, "paradigm": "symbolic"}
            except:
                return {"success": False, "result": None, "paradigm": "symbolic"}

        elif isinstance(input_data, dict) and "premises" in input_data:
            # Resolución lógica
            premises = input_data.get("premises", [])
            conclusion = input_data.get("conclusion", "")
            result = self.logic_solver.solve_propositional_logic(premises, conclusion)
            return {"success": result["valid"], "result": result, "paradigm": "symbolic"}

        return {"success": False, "result": None, "paradigm": "symbolic"}

    def _execute_associative_memory(self, task: str, input_data: Any, context: Dict[str, Any]) -> Any:
        """Ejecuta paradigma de memoria asociativa"""
        if isinstance(input_data, (list, np.ndarray)):
            if isinstance(input_data, list):
                input_vector = np.array(input_data)
            else:
                input_vector = input_data

            # Asegurar tamaño correcto
            if len(input_vector.shape) == 1:
                input_vector = input_vector.reshape(1, -1)

            # Ajustar a 768 dimensiones si es necesario
            if input_vector.shape[1] != 768:
                input_vector = np.resize(input_vector, (input_vector.shape[0], 768))

            result = self.associative_memory.retrieve_pattern(input_vector[0], k=5)
            return {"success": True, "result": result, "paradigm": "associative_memory"}

        return {"success": False, "result": None, "paradigm": "associative_memory"}

    def _execute_deterministic(self, task: str, input_data: Any, context: Dict[str, Any]) -> Any:
        """Ejecuta paradigma determinista"""
        if task.lower() in ["buscar", "search"]:
            if isinstance(input_data, dict):
                arr = input_data.get("array", [])
                target = input_data.get("target")
                algorithm = input_data.get("algorithm", "binary_search")
                result = self.deterministic_engine.execute_algorithm(
                    AlgorithmType.SEARCH, algorithm, arr=arr, target=target
                )
                return result

        elif task.lower() in ["ordenar", "sort"]:
            if isinstance(input_data, list):
                algorithm = input_data[1] if len(input_data) > 1 else "quick_sort"
                arr = input_data[0] if isinstance(input_data[0], list) else input_data
                result = self.deterministic_engine.execute_algorithm(
                    AlgorithmType.SORTING, algorithm, arr=arr
                )
                return result

        elif task.lower() in ["camino", "path", "ruta"]:
            if isinstance(input_data, dict):
                graph = input_data.get("graph", {})
                start = input_data.get("start")
                end = input_data.get("end")
                algorithm = input_data.get("algorithm", "dijkstra")
                heuristic = input_data.get("heuristic", lambda x, y: 0)
                result = self.deterministic_engine.execute_algorithm(
                    AlgorithmType.PATHFINDING, algorithm,
                    graph=graph, start=start, end=end, heuristic=heuristic
                )
                return result

        return {"success": False, "result": None, "paradigm": "deterministic"}

    def _execute_llm(self, task: str, input_data: Any, context: Dict[str, Any]) -> Any:
        """Ejecuta paradigma LLM con validación anti-alucinaciones"""
        if isinstance(input_data, str):
            # Validar salida de LLM
            validation = self.anti_hallucination.validate_llm_output(input_data)

            if validation.is_hallucination:
                # Corregir alucinaciones
                corrected = self.hallucination_corrector.correct_llm_response(input_data)
                return {
                    "success": True,
                    "result": corrected["corrected"],
                    "paradigm": "llm",
                    "was_hallucination": True,
                    "original": input_data,
                    "confidence": corrected["confidence"]
                }
            else:
                return {
                    "success": True,
                    "result": input_data,
                    "paradigm": "llm",
                    "was_hallucination": False,
                    "confidence": validation.confidence_score
                }

        return {"success": False, "result": None, "paradigm": "llm"}

    def _execute_graph(self, task: str, input_data: Any, context: Dict[str, Any]) -> Any:
        """Ejecuta paradigma de grafos"""
        # Usar grafo existente del cognitive core
        try:
            from knowledge_graph import KnowledgeGraph
            graph = KnowledgeGraph()

            # Si el grafo no está inicializado, inicializarlo
            if not graph.is_healthy():
                return {"success": False, "result": None, "paradigm": "graph"}

            # Consultar grafo
            if isinstance(input_data, str):
                relations = graph.query_relations(input_data, [])
                return {"success": True, "result": relations, "paradigm": "graph"}

        except:
            pass

        return {"success": False, "result": None, "paradigm": "graph"}

    def _execute_hybrid(self, task: str, input_data: Any, context: Dict[str, Any]) -> Any:
        """Ejecuta paradigma híbrido combinando todos"""
        results = {}

        # Ejecutar todos los paradigmas
        paradigms = [
            Paradigm.DETERMINISTIC,
            Paradigm.SYMBOLIC,
            Paradigm.ASSOCIATIVE_MEMORY,
            Paradigm.DEEP_LEARNING,
            Paradigm.GRAPH
        ]

        for paradigm in paradigms:
            try:
                result = self._execute_paradigm(paradigm, task, input_data, context)
                results[paradigm.value] = result
            except:
                continue

        # Combinar resultados
        successful_results = {k: v for k, v in results.items() if v.get("success", False)}

        if successful_results:
            # Priorizar resultados deterministas
            if "deterministic" in successful_results:
                return successful_results["deterministic"]
            elif "symbolic" in successful_results:
                return successful_results["symbolic"]
            else:
                return list(successful_results.values())[0]

        return {"success": False, "result": None, "paradigm": "hybrid"}

    def _validate_result(self, result: Any, paradigm: Paradigm) -> bool:
        """Valida el resultado de un paradigma"""
        if not result:
            return False

        if isinstance(result, dict):
            # Validación anti-alucinaciones para LLM
            if paradigm == Paradigm.LLM:
                return not result.get("was_hallucination", False)

            # Validación básica para otros paradigmas
            return result.get("success", False)

        return True

    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado del sistema neuro-simbólico"""
        return {
            "deep_learning": {
                "active_networks": self.deep_learning.list_networks(),
                "status": "active" if self.deep_learning.active_networks else "inactive"
            },
            "symbolic": {
                "symbols_count": len(self.symbolic_reasoner.symbols),
                "facts_count": len(self.symbolic_reasoner.facts),
                "rules_count": len(self.symbolic_reasoner.rules),
                "status": "active"
            },
            "associative_memory": self.associative_memory.get_memory_statistics(),
            "deterministic": {
                "available_algorithms": self.deterministic_engine.get_available_algorithms(),
                "status": "active"
            },
            "anti_hallucination": self.anti_hallucination.get_validation_statistics(),
            "process_history": {
                "total_processes": len(self.process_history),
                "recent": [
                    {
                        "task": p.task,
                        "paradigms": [par.value for par in p.paradigms_used],
                        "confidence": p.confidence,
                        "validation_passed": p.validation_passed,
                        "execution_time": p.execution_time
                    }
                    for p in self.process_history[-10:]
                ]
            },
            "paradigm_priorities": {
                paradigm.value: priority
                for paradigm, priority in self.paradigm_priorities.items()
            }
        }

    def add_domain_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """Agrega conocimiento de dominio al sistema"""
        # Agregar a razonador simbólico
        if "facts" in knowledge:
            for fact in knowledge["facts"]:
                self.hallucination_corrector.add_domain_knowledge([fact])

        # Agregar a memoria asociativa
        if "patterns" in knowledge:
            for pattern in knowledge["patterns"]:
                vector = np.array(pattern.get("vector", [0] * 768))
                label = pattern.get("label", "unknown")
                metadata = pattern.get("metadata", {})
                self.associative_memory.store_pattern(vector, label, metadata)

    def configure_paradigm_priorities(self, priorities: Dict[Paradigm, float]) -> None:
        """Configura las prioridades de los paradigmas"""
        for paradigm, priority in priorities.items():
            if 0.0 <= priority <= 1.0:
                self.paradigm_priorities[paradigm] = priority


# Instancia global del motor neuro-simbólico
neuro_symbolic_engine = NeuroSymbolicEngine()
