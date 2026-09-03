"""
Sistema Backend Autónomo Controlado

Este sistema puede tomar decisiones autónomas dentro de límites predefinidos,
pero siempre con mecanismos de seguridad y control humano.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import json


class AutonomyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AutonomousAgentConfig:
    """Configuración del agente autónomo"""
    autonomy_level: AutonomyLevel = AutonomyLevel.MEDIUM
    max_autonomous_actions: int = 50
    action_time_limit: int = 30  # segundos
    human_approval_required: bool = True
    monitoring_enabled: bool = True
    emergency_stop: bool = True
    max_resource_usage: int = 80  # 80% de recursos máximos
    allowed_actions: List[str] = field(default_factory=lambda: [
        'generate_plan',
        'optimize_tasks',
        'send_reminder',
        'analyze_progress',
        'log_activity',
        'calculate_statistics'
    ])
    forbidden_actions: List[str] = field(default_factory=lambda: [
        'delete_user_data',
        'modify_system_config',
        'access_sensitive_data'
    ])


@dataclass
class Action:
    """Representa una acción a ejecutar"""
    id: str
    type: str
    description: str
    parameters: Dict[str, Any]
    requires_approval: bool
    risk_level: RiskLevel
    timestamp: datetime


@dataclass
class ActionResult:
    """Resultado de una acción ejecutada"""
    success: bool
    result: Any
    error: Optional[str] = None
    requires_human_intervention: bool = False
    monitored: bool = False


class AutonomousAgent:
    """Agente autónomo con límites de seguridad"""

    def __init__(self, config: AutonomousAgentConfig):
        self.config = config
        self.action_history: List[Action] = []
        self.action_count: int = 0
        self.is_active: bool = True
        self.emergency_stop_triggered: bool = False
        self._validate_config()

    def _validate_config(self) -> None:
        """Valida la configuración del agente"""
        if self.config.autonomy_level == AutonomyLevel.HIGH and not self.config.human_approval_required:
            raise ValueError('High autonomy requires human approval for critical actions')

        if self.config.max_autonomous_actions <= 0:
            raise ValueError('Max autonomous actions must be greater than 0')

    def _can_execute_autonomously(self, action: Action) -> bool:
        """Evalúa si una acción puede ser ejecutada autónomamente"""
        # Verificar parada de emergencia
        if self.emergency_stop_triggered:
            return False

        # Verificar límites de acción
        if self.action_count >= self.config.max_autonomous_actions:
            return False

        # Verificar nivel de autonomía
        if action.risk_level == RiskLevel.HIGH and self.config.autonomy_level != AutonomyLevel.HIGH:
            return False

        # Verificar acciones permitidas
        if action.type not in self.config.allowed_actions:
            return False

        # Verificar acciones prohibidas
        if action.type in self.config.forbidden_actions:
            return False

        return True

    async def execute_action(self, action: Action) -> ActionResult:
        """Ejecuta una acción con evaluación de autonomía"""
        # Verificar si el sistema está activo
        if not self.is_active:
            return ActionResult(
                success=False,
                result=None,
                error='Agent is not active',
                requires_human_intervention=True,
                monitored=False
            )

        # Verificar parada de emergencia
        if self.emergency_stop_triggered:
            return ActionResult(
                success=False,
                result=None,
                error='Emergency stop triggered',
                requires_human_intervention=True,
                monitored=True
            )

        # Evaluar autonomía
        can_execute_autonomously = self._can_execute_autonomously(action)

        # Si requiere aprobación humana y no puede ser autónoma
        if action.requires_approval and not can_execute_autonomously:
            self._log_action(action, 'pending_approval')
            return ActionResult(
                success=False,
                result=None,
                error='Action requires human approval',
                requires_human_intervention=True,
                monitored=self.config.monitoring_enabled
            )

        try:
            # Ejecutar acción
            result = await self._perform_action(action)

            # Incrementar contador de acciones
            self.action_count += 1

            # Log de acción
            self._log_action(action, 'completed')

            return ActionResult(
                success=True,
                result=result,
                requires_human_intervention=False,
                monitored=self.config.monitoring_enabled
            )
        except Exception as error:
            self._log_action(action, 'failed')
            return ActionResult(
                success=False,
                result=None,
                error=str(error),
                requires_human_intervention=True,
                monitored=self.config.monitoring_enabled
            )

    async def _perform_action(self, action: Action) -> Any:
        """Realiza la acción específica"""
        # Aquí implementaríamos la lógica específica de cada acción
        action_handlers = {
            'generate_plan': self._generate_plan,
            'optimize_tasks': self._optimize_tasks,
            'send_reminder': self._send_reminder,
            'analyze_progress': self._analyze_progress
        }

        handler = action_handlers.get(action.type)
        if handler:
            return await handler(action.parameters)
        else:
            raise ValueError(f'Unknown action type: {action.type}')

    async def _generate_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lógica para generar planes autónomamente"""
        return {'plan': 'autogenerated_plan', 'confidence': 0.85}

    async def _optimize_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lógica para optimizar tareas"""
        return {'optimized': True, 'improvements': 5}

    async def _send_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lógica para enviar recordatorios"""
        return {'sent': True, 'recipient': params.get('userId')}

    async def _analyze_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lógica para analizar progreso"""
        return {'progress': 75, 'recommendations': ['speed_up', 'focus']}

    def _log_action(self, action: Action, status: str) -> None:
        """Sistema de logging"""
        action_copy = Action(
            id=action.id,
            type=action.type,
            description=action.description,
            parameters=action.parameters,
            requires_approval=action.requires_approval,
            risk_level=action.risk_level,
            timestamp=datetime.now()
        )
        self.action_history.append(action_copy)

        if self.config.monitoring_enabled:
            print(f'[AGENT LOG] Action: {action.type}, Status: {status}, Time: {datetime.now().isoformat()}')

    def trigger_emergency_stop(self) -> None:
        """Control de emergencia"""
        self.emergency_stop_triggered = True
        self.is_active = False
        print('[EMERGENCY STOP] Agent deactivated immediately')

    def reactivate(self) -> None:
        """Reactivar el agente"""
        self.emergency_stop_triggered = False
        self.is_active = True
        self.action_count = 0
        print('[AGENT REACTIVATED] Agent is now active')

    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del agente"""
        return {
            'is_active': self.is_active,
            'action_count': self.action_count,
            'remaining_actions': self.config.max_autonomous_actions - self.action_count,
            'emergency_stop_triggered': self.emergency_stop_triggered,
            'recent_actions': [
                {
                    'id': a.id,
                    'type': a.type,
                    'description': a.description,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in self.action_history[-10:]
            ]
        }

    def reset_action_count(self) -> None:
        """Reiniciar contador de acciones"""
        self.action_count = 0
        print('[AGENT] Action count reset')


# Configuración inicial del agente
agent_config = AutonomousAgentConfig()
autonomous_agent = AutonomousAgent(agent_config)
