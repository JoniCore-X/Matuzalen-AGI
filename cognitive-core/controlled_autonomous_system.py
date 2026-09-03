"""
Sistema Backend Autónomo Controlado - Integración Principal

Este archivo integra todos los componentes del sistema autónomo:
- Agente autónomo con límites
- Motor de toma de decisiones
- Monitor de seguridad
- Sistema de control humano
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from autonomous_agent import (
    AutonomousAgent, AutonomousAgentConfig, Action, ActionResult, RiskLevel
)
from decision_engine import (
    DecisionEngine, DecisionContext, DecisionOption, Decision, Urgency
)
from safety_monitor import SafetyMonitor, SafetyCheckResult, ResourceUsage


@dataclass
class ProcessRequestResult:
    """Resultado de procesamiento de solicitud"""
    success: bool
    result: Any
    decision: Optional[Decision] = None
    safety_check: Optional[SafetyCheckResult] = None
    requires_human_approval: bool = False


class ControlledAutonomousSystem:
    """Sistema Principal Autónomo Controlado"""

    def __init__(self):
        self.is_active: bool = False
        self.human_controller: Optional[str] = None
        self.system_logs: List[str] = []

    async def start(self, controller_id: str) -> None:
        """Inicia el sistema autónomo"""
        self.human_controller = controller_id
        self.is_active = True
        self._log(f'System started by human controller: {controller_id}')
        print('[SYSTEM] Autonomous system started with safety controls')

    async def stop(self, controller_id: str) -> None:
        """Detiene el sistema autónomo"""
        if self.human_controller != controller_id:
            raise Exception('Unauthorized: Only the controller can stop the system')

        self.is_active = False
        autonomous_agent.trigger_emergency_stop()
        self._log(f'System stopped by human controller: {controller_id}')
        print('[SYSTEM] Autonomous system stopped')

    async def process_request(self, request: Dict[str, Any]) -> ProcessRequestResult:
        """Procesa una solicitud autónoma"""
        if not self.is_active:
            return ProcessRequestResult(
                success=False,
                result=None,
                requires_human_approval=True
            )

        self._log(f"Processing request: {request.get('type')}")

        try:
            # 1. Crear contexto de decisión
            context = DecisionContext(
                situation=request.get('type', ''),
                data=request.get('data', {}),
                urgency=Urgency(request.get('urgency', 'medium')),
                confidence=0.8,
                alternatives=self._generate_alternatives(request)
            )

            # 2. Motor de toma de decisiones
            decision = await decision_engine.make_decision(context)

            # 3. Verificación de seguridad
            action = Action(
                id=f"action-{int(datetime.now().timestamp() * 1000000)}",
                type=decision.selected_option.action,
                description=decision.selected_option.description,
                parameters=request.get('data', {}),
                requires_approval=decision.requires_human_approval,
                risk_level=decision.selected_option.risk_level,
                timestamp=datetime.now()
            )

            action_dict = {
                'id': action.id,
                'type': action.type,
                'description': action.description,
                'parameters': action.parameters,
                'requires_approval': action.requires_approval,
                'risk_level': action.risk_level.value,
                'timestamp': action.timestamp.isoformat()
            }

            safety_check = await safety_monitor.monitor_action(action_dict)

            if not safety_check.allowed:
                self._log(f"Action blocked by safety monitor: {', '.join(safety_check.criticals)}")
                return ProcessRequestResult(
                    success=False,
                    result=None,
                    decision=decision,
                    safety_check=safety_check,
                    requires_human_approval=True
                )

            # 4. Ejecutar acción si pasa seguridad
            if decision.requires_human_approval:
                self._log(f"Action requires human approval: {action.type}")
                return ProcessRequestResult(
                    success=False,
                    result=None,
                    decision=decision,
                    safety_check=safety_check,
                    requires_human_approval=True
                )

            result = await autonomous_agent.execute_action(action)

            self._log(f"Action completed successfully: {action.type}")
            return ProcessRequestResult(
                success=result.success,
                result=result.result,
                decision=decision,
                safety_check=safety_check,
                requires_human_approval=False
            )

        except Exception as error:
            self._log(f"Error processing request: {error}")
            return ProcessRequestResult(
                success=False,
                result=None,
                requires_human_approval=True
            )

    def _generate_alternatives(self, request: Dict[str, Any]) -> List[DecisionOption]:
        """Genera alternativas para una solicitud"""
        request_type = request.get('type', '')

        if request_type == 'generate_plan':
            return [
                DecisionOption(
                    action='generate_plan',
                    description='Generar plan automáticamente',
                    risk_level=RiskLevel.LOW,
                    expected_outcome='Plan generado con IA',
                    confidence=0.85
                ),
                DecisionOption(
                    action='request_human_input',
                    description='Solicitar input humano',
                    risk_level=RiskLevel.LOW,
                    expected_outcome='Plan basado en input humano',
                    confidence=0.95
                )
            ]
        elif request_type == 'optimize_tasks':
            return [
                DecisionOption(
                    action='optimize_tasks',
                    description='Optimizar tareas automáticamente',
                    risk_level=RiskLevel.MEDIUM,
                    expected_outcome='Tareas reorganizadas',
                    confidence=0.75
                ),
                DecisionOption(
                    action='suggest_optimizations',
                    description='Sugerir optimizaciones',
                    risk_level=RiskLevel.LOW,
                    expected_outcome='Sugerencias presentadas',
                    confidence=0.90
                )
            ]
        else:
            return [
                DecisionOption(
                    action='proceed_autonomously',
                    description='Proceder autónomamente',
                    risk_level=RiskLevel.MEDIUM,
                    expected_outcome='Acción completada',
                    confidence=0.70
                ),
                DecisionOption(
                    action='request_approval',
                    description='Solicitar aprobación',
                    risk_level=RiskLevel.LOW,
                    expected_outcome='Esperar aprobación',
                    confidence=0.95
                )
            ]

    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del sistema"""
        return {
            'is_active': self.is_active,
            'controller': self.human_controller,
            'agent_status': autonomous_agent.get_status(),
            'decision_stats': decision_engine.get_decision_stats(),
            'safety_status': safety_monitor.get_safety_status(),
            'recent_logs': self.system_logs[-20:]
        }

    async def approve_action(self, action_id: str, controller_id: str) -> bool:
        """Aprobación humana de acción pendiente"""
        if self.human_controller != controller_id:
            raise Exception('Unauthorized')

        self._log(f"Action approved by human: {action_id}")
        return True

    async def reject_action(self, action_id: str, controller_id: str) -> bool:
        """Rechazo humano de acción pendiente"""
        if self.human_controller != controller_id:
            raise Exception('Unauthorized')

        self._log(f"Action rejected by human: {action_id}")
        return True

    def _log(self, message: str) -> None:
        """Sistema de logging"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.system_logs.append(log_entry)
        print(log_entry)

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Actualizar configuración del sistema"""
        # Aquí se implementaría la lógica para actualizar configuración
        self._log('System configuration updated')


# Instancia del sistema principal
autonomous_system = ControlledAutonomousSystem()


class AutonomousAPI:
    """API del sistema autónomo"""

    @staticmethod
    async def start(controller_id: str) -> None:
        """Control del sistema - iniciar"""
        await autonomous_system.start(controller_id)

    @staticmethod
    async def stop(controller_id: str) -> None:
        """Control del sistema - detener"""
        await autonomous_system.stop(controller_id)

    @staticmethod
    async def process_request(request: Dict[str, Any]) -> ProcessRequestResult:
        """Procesamiento de solicitudes"""
        return await autonomous_system.process_request(request)

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Estado y monitoreo"""
        return autonomous_system.get_system_status()

    @staticmethod
    async def approve_action(action_id: str, controller_id: str) -> bool:
        """Control humano - aprobar"""
        return await autonomous_system.approve_action(action_id, controller_id)

    @staticmethod
    async def reject_action(action_id: str, controller_id: str) -> bool:
        """Control humano - rechazar"""
        return await autonomous_system.reject_action(action_id, controller_id)

    @staticmethod
    def update_config(config: Dict[str, Any]) -> None:
        """Configuración"""
        autonomous_system.update_config(config)


# Exportar clases y funciones principales
__all__ = [
    'ControlledAutonomousSystem',
    'autonomous_system',
    'AutonomousAPI',
    'ProcessRequestResult'
]
