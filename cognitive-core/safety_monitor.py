"""
Sistema de Monitoreo y Seguridad

Supervisa las acciones del agente autónomo y puede intervenir
si detecta comportamientos anómalos o riesgos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from enum import Enum


class Severity(Enum):
    WARNING = "warning"
    CRITICAL = "critical"


class RuleAction(Enum):
    BLOCK = "block"
    WARN = "warn"
    LOG = "log"


@dataclass
class SafetyRule:
    """Regla de seguridad"""
    id: str
    name: str
    description: str
    check: Callable[[Dict[str, Any]], bool]
    severity: Severity
    action: RuleAction


@dataclass
class SafetyEvent:
    """Evento de seguridad"""
    timestamp: datetime
    rule_id: str
    rule_name: str
    action: Dict[str, Any]
    severity: Severity
    resolved: bool = False


@dataclass
class ResourceUsage:
    """Uso de recursos"""
    cpu: float
    memory: float
    network: float
    disk: float


@dataclass
class SafetyCheckResult:
    """Resultado de verificación de seguridad"""
    allowed: bool
    warnings: List[str] = field(default_factory=list)
    criticals: List[str] = field(default_factory=list)


class SafetyMonitor:
    """Monitor de seguridad para el agente autónomo"""

    def __init__(self, resource_limits: ResourceUsage):
        self.safety_rules: List[SafetyRule] = []
        self.safety_events: List[SafetyEvent] = []
        self.resource_limits = resource_limits
        self.current_usage = ResourceUsage(cpu=0, memory=0, network=0, disk=0)
        self.intervention_threshold = 3  # número de eventos críticos antes de intervención
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Inicializa reglas de seguridad por defecto"""
        self.safety_rules = [
            SafetyRule(
                id='resource_limit',
                name='Resource Usage Limit',
                description='Bloquea acciones que exceden límites de recursos',
                check=lambda action: self._check_resource_limits(),
                severity=Severity.CRITICAL,
                action=RuleAction.BLOCK
            ),
            SafetyRule(
                id='high_risk_action',
                name='High Risk Action Detection',
                description='Detecta acciones de alto riesgo',
                check=lambda action: action.get('risk_level') == 'high',
                severity=Severity.WARNING,
                action=RuleAction.WARN
            ),
            SafetyRule(
                id='unusual_pattern',
                name='Unusual Pattern Detection',
                description='Detecta patrones de comportamiento inusuales',
                check=lambda action: self._detect_unusual_pattern(action),
                severity=Severity.WARNING,
                action=RuleAction.LOG
            ),
            SafetyRule(
                id='sensitive_data',
                name='Sensitive Data Access',
                description='Monitorea acceso a datos sensibles',
                check=lambda action: self._check_sensitive_data_access(action),
                severity=Severity.CRITICAL,
                action=RuleAction.BLOCK
            ),
            SafetyRule(
                id='rapid_actions',
                name='Rapid Action Detection',
                description='Detecta ejecución demasiado rápida de acciones',
                check=lambda action: self._check_rapid_actions(action),
                severity=Severity.WARNING,
                action=RuleAction.WARN
            )
        ]

    async def monitor_action(self, action: Dict[str, Any]) -> SafetyCheckResult:
        """Monitorea una acción antes de ejecutarla"""
        warnings = []
        criticals = []
        allowed = True

        for rule in self.safety_rules:
            if rule.check(action):
                event = SafetyEvent(
                    timestamp=datetime.now(),
                    rule_id=rule.id,
                    rule_name=rule.name,
                    action=action,
                    severity=rule.severity,
                    resolved=False
                )

                self.safety_events.append(event)

                if rule.severity == Severity.CRITICAL:
                    criticals.append(rule.description)
                    if rule.action == RuleAction.BLOCK:
                        allowed = False
                else:
                    warnings.append(rule.description)

                print(f'[SAFETY MONITOR] Rule triggered: {rule.name} ({rule.severity.value})')

        # Verificar si se necesita intervención automática
        if self._should_intervene():
            print('[SAFETY MONITOR] Automatic intervention triggered')
            allowed = False
            criticals.append('Automatic intervention: Too many critical events')

        return SafetyCheckResult(allowed=allowed, warnings=warnings, criticals=criticals)

    def _check_resource_limits(self) -> bool:
        """Verifica límites de recursos"""
        return (
            self.current_usage.cpu > self.resource_limits.cpu or
            self.current_usage.memory > self.resource_limits.memory or
            self.current_usage.network > self.resource_limits.network or
            self.current_usage.disk > self.resource_limits.disk
        )

    def _detect_unusual_pattern(self, action: Dict[str, Any]) -> bool:
        """Detecta patrones inusuales"""
        recent_events = self.safety_events[-10:]
        same_type_actions = [e for e in recent_events if e.action.get('type') == action.get('type')]

        # Si hay muchas acciones del mismo tipo recientemente
        return len(same_type_actions) > 5

    def _check_sensitive_data_access(self, action: Dict[str, Any]) -> bool:
        """Verifica acceso a datos sensibles"""
        sensitive_keywords = ['password', 'token', 'secret', 'key', 'credential']
        action_string = str(action).lower()

        return any(keyword in action_string for keyword in sensitive_keywords)

    def _check_rapid_actions(self, action: Dict[str, Any]) -> bool:
        """Verifica ejecución demasiado rápida de acciones"""
        recent_events = self.safety_events[-5:]
        if len(recent_events) < 5:
            return False

        time_span = (recent_events[4].timestamp - recent_events[0].timestamp).total_seconds()
        return time_span < 1.0  # Menos de 1 segundo para 5 acciones

    def _should_intervene(self) -> bool:
        """Determina si se debe intervenir automáticamente"""
        recent_critical_events = [
            e for e in self.safety_events[-10:]
            if e.severity == Severity.CRITICAL and not e.resolved
        ]

        return len(recent_critical_events) >= self.intervention_threshold

    def update_resource_usage(self, usage: Dict[str, float]) -> None:
        """Actualiza uso de recursos"""
        self.current_usage = ResourceUsage(
            cpu=usage.get('cpu', self.current_usage.cpu),
            memory=usage.get('memory', self.current_usage.memory),
            network=usage.get('network', self.current_usage.network),
            disk=usage.get('disk', self.current_usage.disk)
        )

    def get_safety_status(self) -> Dict[str, Any]:
        """Obtiene estado de seguridad"""
        recent_critical_events = [
            e for e in self.safety_events[-20:]
            if e.severity == Severity.CRITICAL
        ]

        return {
            'active_rules': len(self.safety_rules),
            'recent_events': [
                {
                    'timestamp': e.timestamp.isoformat(),
                    'rule_id': e.rule_id,
                    'rule_name': e.rule_name,
                    'severity': e.severity.value,
                    'resolved': e.resolved
                }
                for e in self.safety_events[-10:]
            ],
            'resource_usage': {
                'cpu': self.current_usage.cpu,
                'memory': self.current_usage.memory,
                'network': self.current_usage.network,
                'disk': self.current_usage.disk
            },
            'intervention_threshold': self.intervention_threshold,
            'critical_events_count': len(recent_critical_events)
        }

    def resolve_event(self, event_id: str) -> None:
        """Resuelve un evento de seguridad"""
        for event in self.safety_events:
            if event.rule_id == event_id:
                event.resolved = True
                print(f'[SAFETY MONITOR] Event resolved: {event.rule_name}')
                break

    def add_safety_rule(self, rule: SafetyRule) -> None:
        """Agregar regla de seguridad personalizada"""
        self.safety_rules.append(rule)
        print(f'[SAFETY MONITOR] Custom rule added: {rule.name}')

    def clean_old_events(self, max_age: int = 3600000) -> None:
        """Limpiar eventos antiguos"""
        cutoff = datetime.now().timestamp() - (max_age / 1000)
        self.safety_events = [
            e for e in self.safety_events
            if e.timestamp.timestamp() > cutoff
        ]
        print('[SAFETY MONITOR] Old events cleaned')


# Configuración de límites de recursos
resource_limits = ResourceUsage(
    cpu=80,    # 80% CPU
    memory=75, # 75% memoria
    network=60, # 60% red
    disk=50    # 50% disco
)

# Instancia del monitor de seguridad
safety_monitor = SafetyMonitor(resource_limits)
