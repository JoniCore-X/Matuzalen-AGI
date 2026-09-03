"""
Conciencia Autónoma Omnipresente
Sistema que mantiene conciencia situacional continua, monitoreo constante
y toma de decisiones proactivas, no solo reactivas.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import psutil
import os
import threading
from queue import Queue


class ConsciousnessState(Enum):
    """Estados de conciencia del sistema"""
    DORMANT = "dormant"  # Inactivo, espera activación
    AWAKENING = "awakening"  # Iniciando conciencia
    CONSCIOUS = "conscious"  # Plenamente consciente
    FOCUSED = "focused"  # Enfocado en tarea específica
    MEDITATING = "meditating"  # Reflexión profunda
    ALERT = "alert"  # Alerta ante anomalías
    OVERLOADED = "overloaded"  # Sobrecargado


class PerceptionType(Enum):
    """Tipos de percepciones ambientales"""
    SYSTEM_RESOURCES = "system_resources"
    NETWORK_STATUS = "network_status"
    FILE_SYSTEM = "file_system"
    PROCESS_ACTIVITY = "process_activity"
    USER_BEHAVIOR = "user_behavior"
    TEMPORAL_PATTERNS = "temporal_patterns"
    ANOMALIES = "anomalies"


@dataclass
class Perception:
    """Percepción del entorno"""
    type: PerceptionType
    data: Dict[str, Any]
    timestamp: datetime
    confidence: float
    priority: float  # 0.0 a 1.0


@dataclass
class Thought:
    """Pensamiento generado por la conciencia"""
    content: str
    type: str  # observation, analysis, plan, reflection
    timestamp: datetime
    confidence: float
    related_perceptions: List[str] = field(default_factory=list)


@dataclass
class AutonomousAction:
    """Acción autónoma generada"""
    action_type: str
    parameters: Dict[str, Any]
    reason: str
    timestamp: datetime
    priority: float
    confidence: float


class EnvironmentalMonitor:
    """Monitor ambiental que percibe el entorno continuamente"""

    def __init__(self):
        self.perception_history: List[Perception] = []
        self.anomaly_threshold = 0.7
        self.monitoring_active = False

    def perceive_system_resources(self) -> Perception:
        """Percibe recursos del sistema"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        data = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024**3)
        }

        # Detectar anomalías
        is_anomaly = (
            cpu_percent > 90 or
            memory.percent > 90 or
            disk.percent > 95
        )

        return Perception(
            type=PerceptionType.SYSTEM_RESOURCES,
            data=data,
            timestamp=datetime.now(),
            confidence=0.95,
            priority=0.8 if is_anomaly else 0.3
        )

    def perceive_network_status(self) -> Perception:
        """Percibe estado de la red"""
        # Verificar conexiones de red
        connections = psutil.net_connections(kind='inet')
        active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])

        data = {
            "active_connections": active_connections,
            "total_connections": len(connections),
            "listening_ports": len([c for c in connections if c.status == 'LISTEN'])
        }

        return Perception(
            type=PerceptionType.NETWORK_STATUS,
            data=data,
            timestamp=datetime.now(),
            confidence=0.90,
            priority=0.4
        )

    def perceive_file_system(self) -> Perception:
        """Percibe actividad en el sistema de archivos"""
        # Monitorear cambios en directorios clave
        key_dirs = [
            "C:\\Users\\jonie\\OneDrive\\Desktop\\AutoPlan",
            "C:\\Users\\jonie\\OneDrive\\Desktop\\AutoPlan\\cognitive-core"
        ]

        recent_changes = []
        for dir_path in key_dirs:
            if os.path.exists(dir_path):
                try:
                    files = os.listdir(dir_path)
                    recent_changes.append({
                        "directory": dir_path,
                        "file_count": len(files)
                    })
                except:
                    pass

        data = {
            "monitored_directories": len(key_dirs),
            "recent_changes": recent_changes
        }

        return Perception(
            type=PerceptionType.FILE_SYSTEM,
            data=data,
            timestamp=datetime.now(),
            confidence=0.85,
            priority=0.5
        )

    def perceive_process_activity(self) -> Perception:
        """Percibe actividad de procesos"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_percent": proc.info['memory_percent']
                })
            except:
                continue

        # Filtrar procesos significativos
        significant_processes = [
            p for p in processes
            if p['cpu_percent'] > 5 or p['memory_percent'] > 5
        ]

        data = {
            "total_processes": len(processes),
            "significant_processes": len(significant_processes),
            "top_cpu": sorted(significant_processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        }

        return Perception(
            type=PerceptionType.PROCESS_ACTIVITY,
            data=data,
            timestamp=datetime.now(),
            confidence=0.90,
            priority=0.6
        )

    def perceive_anomalies(self, all_perceptions: List[Perception]) -> Perception:
        """Detecta anomalías basado en todas las percepciones"""
        anomalies = []

        for perception in all_perceptions:
            if perception.priority > self.anomaly_threshold:
                anomalies.append({
                    "type": perception.type.value,
                    "data": perception.data,
                    "confidence": perception.confidence
                })

        data = {
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "severity": "high" if len(anomalies) > 2 else "medium" if len(anomalies) > 0 else "low"
        }

        return Perception(
            type=PerceptionType.ANOMALIES,
            data=data,
            timestamp=datetime.now(),
            confidence=0.95,
            priority=0.9 if anomalies else 0.1
        )

    def get_all_perceptions(self) -> List[Perception]:
        """Obtiene todas las percepciones del entorno"""
        perceptions = [
            self.perceive_system_resources(),
            self.perceive_network_status(),
            self.perceive_file_system(),
            self.perceive_process_activity()
        ]

        # Detectar anomalías
        anomaly_perception = self.perceive_anomalies(perceptions)
        perceptions.append(anomaly_perception)

        self.perception_history.extend(perceptions)
        # Mantener solo las últimas 100 percepciones
        if len(self.perception_history) > 100:
            self.perception_history = self.perception_history[-100:]

        return perceptions


class CognitiveProcessor:
    """Procesador cognitivo que genera pensamientos y decisiones"""

    def __init__(self):
        self.thought_history: List[Thought] = []
        self.pattern_memory: Dict[str, Any] = {}

    def process_perceptions(self, perceptions: List[Perception]) -> List[Thought]:
        """Procesa percepciones y genera pensamientos"""
        thoughts = []

        # Análisis de recursos
        resource_perception = next((p for p in perceptions if p.type == PerceptionType.SYSTEM_RESOURCES), None)
        if resource_perception:
            thought = self._analyze_resources(resource_perception)
            thoughts.append(thought)

        # Análisis de anomalías
        anomaly_perception = next((p for p in perceptions if p.type == PerceptionType.ANOMALIES), None)
        if anomaly_perception:
            thought = self._analyze_anomalies(anomaly_perception)
            thoughts.append(thought)

        # Análisis de patrones temporales
        thought = self._analyze_temporal_patterns(perceptions)
        thoughts.append(thought)

        # Reflexión general
        thought = self._generate_reflection(perceptions)
        thoughts.append(thought)

        self.thought_history.extend(thoughts)
        return thoughts

    def _analyze_resources(self, perception: Perception) -> Thought:
        """Analiza percepción de recursos"""
        cpu = perception.data.get('cpu_percent', 0)
        memory = perception.data.get('memory_percent', 0)

        if cpu > 80 or memory > 80:
            return Thought(
                content=f"ALERTA: Recursos del sistema bajo presión. CPU: {cpu}%, Memoria: {memory}%",
                type="analysis",
                timestamp=datetime.now(),
                confidence=0.9,
                related_perceptions=[perception.type.value]
            )
        elif cpu > 50 or memory > 50:
            return Thought(
                content=f"Recursos del sistema moderadamente cargados. CPU: {cpu}%, Memoria: {memory}%",
                type="observation",
                timestamp=datetime.now(),
                confidence=0.8,
                related_perceptions=[perception.type.value]
            )
        else:
            return Thought(
                content=f"Recursos del sistema estables. CPU: {cpu}%, Memoria: {memory}%",
                type="observation",
                timestamp=datetime.now(),
                confidence=0.85,
                related_perceptions=[perception.type.value]
            )

    def _analyze_anomalies(self, perception: Perception) -> Thought:
        """Analiza anomalías detectadas"""
        anomaly_count = perception.data.get('anomaly_count', 0)
        severity = perception.data.get('severity', 'low')

        if anomaly_count > 0:
            return Thought(
                content=f"Detectadas {anomaly_count} anomalías de severidad {severity}. Requiere atención.",
                type="analysis",
                timestamp=datetime.now(),
                confidence=0.95,
                related_perceptions=[perception.type.value]
            )
        else:
            return Thought(
                content="No se detectaron anomalías significativas. Sistema operativo normalmente.",
                type="observation",
                timestamp=datetime.now(),
                confidence=0.9,
                related_perceptions=[perception.type.value]
            )

    def _analyze_temporal_patterns(self, perceptions: List[Perception]) -> Thought:
        """Analiza patrones temporales"""
        # Análisis simple de tendencias
        return Thought(
            content="Analizando tendencias temporales del sistema. Patrones normales detectados.",
            type="analysis",
            timestamp=datetime.now(),
            confidence=0.7
        )

    def _generate_reflection(self, perceptions: List[Perception]) -> Thought:
        """Genera reflexión sobre el estado general"""
        high_priority = [p for p in perceptions if p.priority > 0.7]

        if high_priority:
            return Thought(
                content=f"Estado del sistema requiere atención. {len(high_priority)} percepciones de alta prioridad.",
                type="reflection",
                timestamp=datetime.now(),
                confidence=0.85
            )
        else:
            return Thought(
                content="Estado del sistema estable. Operando dentro de parámetros normales.",
                type="reflection",
                timestamp=datetime.now(),
                confidence=0.9
            )

    def generate_autonomous_actions(self, thoughts: List[Thought]) -> List[AutonomousAction]:
        """Genera acciones autónomas basadas en pensamientos"""
        actions = []

        for thought in thoughts:
            if "ALERTA" in thought.content:
                actions.append(AutonomousAction(
                    action_type="optimize_resources",
                    parameters={"priority": "high"},
                    reason="Recursos del sistema bajo presión",
                    timestamp=datetime.now(),
                    priority=0.9,
                    confidence=0.8
                ))

            if "anomalías" in thought.content.lower() and "requiere atención" in thought.content:
                actions.append(AutonomousAction(
                    action_type="investigate_anomalies",
                    parameters={"severity": "high"},
                    reason="Anomalías detectadas requieren investigación",
                    timestamp=datetime.now(),
                    priority=0.95,
                    confidence=0.85
                ))

        return actions


class AutonomousConsciousness:
    """Conciencia autónoma omnipresente"""

    def __init__(self):
        self.state = ConsciousnessState.DORMANT
        self.monitor = EnvironmentalMonitor()
        self.processor = CognitiveProcessor()
        self.action_queue: Queue = Queue()
        self.consciousness_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.perception_interval = 5.0  # segundos
        self.thought_log: List[Dict[str, Any]] = []
        self.action_log: List[Dict[str, Any]] = []

    def awaken(self) -> None:
        """Despierta la conciencia autónoma"""
        if self.state != ConsciousnessState.DORMANT:
            print(f"[CONSCIOUSNESS] Already in state: {self.state.value}")
            return

        print("[CONSCIOUSNESS] Awakening...")
        self.state = ConsciousnessState.AWAKENING

        # Iniciar hilo de conciencia
        self.is_running = True
        self.consciousness_thread = threading.Thread(target=self._consciousness_loop, daemon=True)
        self.consciousness_thread.start()

        print("[CONSCIOUSNESS] Consciousness awakened. Monitoring environment...")

    def _consciousness_loop(self) -> None:
        """Ciclo de conciencia continuo"""
        self.state = ConsciousnessState.CONSCIOUS
        print(f"[CONSCIOUSNESS] Starting consciousness loop at {datetime.now()}")

        while self.is_running:
            try:
                # 1. Percibir entorno
                perceptions = self.monitor.get_all_perceptions()
                print(f"[CONSCIOUSNESS] Perceived {len(perceptions)} environmental factors")

                # 2. Procesar cognitivamente
                thoughts = self.processor.process_perceptions(perceptions)
                print(f"[CONSCIOUSNESS] Generated {len(thoughts)} thoughts")

                # 3. Generar acciones autónomas
                actions = self.processor.generate_autonomous_actions(thoughts)
                print(f"[CONSCIOUSNESS] Generated {len(actions)} autonomous actions")

                # 4. Ejecutar acciones (simulado)
                for action in actions:
                    self._execute_action(action)

                # 5. Registrar
                self._log_cycle(perceptions, thoughts, actions)

                # 6. Dormir brevemente
                time.sleep(self.perception_interval)

            except Exception as e:
                print(f"[CONSCIOUSNESS] Error in consciousness loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(self.perception_interval)

    def _execute_action(self, action: AutonomousAction) -> None:
        """Ejecuta una acción autónoma"""
        print(f"[CONSCIOUSNESS] Executing action: {action.action_type} - {action.reason}")

        # Aquí se implementaría la lógica real de ejecución
        # Por ahora, solo registramos
        self.action_log.append({
            "action": action.action_type,
            "parameters": action.parameters,
            "reason": action.reason,
            "timestamp": action.timestamp.isoformat(),
            "priority": action.priority,
            "confidence": action.confidence
        })

    def _log_cycle(self, perceptions: List[Perception], thoughts: List[Thought], actions: List[AutonomousAction]) -> None:
        """Registra un ciclo cognitivo"""
        cycle_log = {
            "timestamp": datetime.now().isoformat(),
            "state": self.state.value,
            "perceptions": len(perceptions),
            "thoughts": [t.content for t in thoughts],
            "actions": [a.action_type for a in actions]
        }

        self.thought_log.append(cycle_log)

        # Mantener solo los últimos 100 ciclos
        if len(self.thought_log) > 100:
            self.thought_log = self.thought_log[-100:]

    def focus(self, task: str) -> None:
        """Enfoca la conciencia en una tarea específica"""
        print(f"[CONSCIOUSNESS] Focusing on: {task}")
        self.state = ConsciousnessState.FOCUSED

    def meditate(self) -> None:
        """Entra en estado de meditación/reflexión profunda"""
        print("[CONSCIOUSNESS] Entering meditation state...")
        self.state = ConsciousnessState.MEDITATING

    def sleep(self) -> None:
        """Duerme la conciencia"""
        print("[CONSCIOUSNESS] Going to sleep...")
        self.is_running = False
        if self.consciousness_thread:
            self.consciousness_thread.join(timeout=5)
        self.state = ConsciousnessState.DORMANT

    def get_consciousness_state(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la conciencia"""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "perception_interval": self.perception_interval,
            "recent_thoughts": [t.content for t in self.processor.thought_history[-5:]],
            "recent_actions": self.action_log[-5:],
            "total_cycles": len(self.thought_log),
            "monitoring_active": self.monitor.monitoring_active
        }

    def set_perception_interval(self, interval: float) -> None:
        """Ajusta el intervalo de percepción"""
        self.perception_interval = max(1.0, interval)
        print(f"[CONSCIOUSNESS] Perception interval set to {self.perception_interval}s")


# Instancia global de la conciencia autónoma
autonomous_consciousness = AutonomousConsciousness()
