"""
Cliente Cognitivo - Interfaz con el Núcleo AGI

Este cliente se comunica con el microservicio de razonamiento
que implementa la memoria vectorial y el grafo de conocimiento.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import httpx
import asyncio


class UrgencyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ThoughtStepType(Enum):
    DOCTRINAL = "doctrinal"
    APOLOGETIC = "apologetic"
    PASTORAL = "pastoral"
    STRATEGIC = "strategic"
    EXPERIENTIAL = "experiential"


@dataclass
class CognitiveRequest:
    """Solicitud al núcleo cognitivo"""
    intention: str
    context: Dict[str, Any]
    urgency: UrgencyLevel
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CognitiveResponse:
    """Respuesta del núcleo cognitivo"""
    decision: str
    reasoning: str
    confidence: float
    requires_human_approval: bool
    related_concepts: List[str]
    risk_level: RiskLevel
    timestamp: str


@dataclass
class ThoughtStep:
    """Paso de razonamiento"""
    type: ThoughtStepType
    content: str


@dataclass
class ThoughtPath:
    """Camino de razonamiento completo"""
    summary: str
    doctrinal_fidelity: float
    persuasive_effectiveness: float
    confidence: float
    steps: List[ThoughtStep]


@dataclass
class ToTResponse:
    """Respuesta del motor Tree of Thoughts"""
    intention: str
    paths_evaluated: int
    selected: Optional[ThoughtPath]
    alternatives: List[ThoughtPath]
    timestamp: str


class CognitiveClient:
    """Cliente para comunicarse con el núcleo cognitivo AGI"""

    def __init__(self, api_url: str = 'http://localhost:8000', timeout: int = 30):
        self.api_url = api_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def process_intention(self, request: CognitiveRequest) -> CognitiveResponse:
        """Envía una intención al núcleo cognitivo y recibe una decisión"""
        try:
            response = await self.client.post(
                f'{self.api_url}/cognitive/process',
                json={
                    'intention': request.intention,
                    'context': request.context,
                    'urgency': request.urgency.value,
                    'metadata': request.metadata
                }
            )
            response.raise_for_status()
            data = response.json()

            return CognitiveResponse(
                decision=data.get('decision', ''),
                reasoning=data.get('reasoning', ''),
                confidence=data.get('confidence', 0.0),
                requires_human_approval=data.get('requires_human_approval', False),
                related_concepts=data.get('related_concepts', []),
                risk_level=RiskLevel(data.get('risk_level', 'medium')),
                timestamp=data.get('timestamp', datetime.now().isoformat())
            )
        except Exception as error:
            print(f'[COGNITIVE CLIENT] Error processing intention: {error}')
            # Fallback a modo local si el servicio no está disponible
            return self._fallback_processing(request)

    def _fallback_processing(self, request: CognitiveRequest) -> CognitiveResponse:
        """Procesamiento de fallback cuando el servicio cognitivo no está disponible"""
        print('[COGNITIVE CLIENT] Using fallback processing')

        return CognitiveResponse(
            decision=f'Fallback decision for: {request.intention}',
            reasoning='Cognitive service unavailable - using local processing',
            confidence=0.5,
            requires_human_approval=request.urgency == UrgencyLevel.HIGH,
            related_concepts=[],
            risk_level=RiskLevel.HIGH if request.urgency == UrgencyLevel.HIGH else RiskLevel.MEDIUM,
            timestamp=datetime.now().isoformat()
        )

    async def tree_of_thoughts(self, intention: str, context: Dict[str, Any] = None) -> Optional[ToTResponse]:
        """Invoca el motor Tree of Thoughts teológico-estratégico"""
        if context is None:
            context = {}

        try:
            response = await self.client.post(
                f'{self.api_url}/cognitive/tot',
                json={'intention': intention, 'context': context}
            )
            response.raise_for_status()
            data = response.json()

            # Convertir pasos de pensamiento
            selected = None
            if data.get('selected'):
                selected_data = data['selected']
                selected = ThoughtPath(
                    summary=selected_data.get('summary', ''),
                    doctrinal_fidelity=selected_data.get('doctrinal_fidelity', 0.0),
                    persuasive_effectiveness=selected_data.get('persuasive_effectiveness', 0.0),
                    confidence=selected_data.get('confidence', 0.0),
                    steps=[
                        ThoughtStep(
                            type=ThoughtStepType(step.get('type', 'strategic')),
                            content=step.get('content', '')
                        )
                        for step in selected_data.get('steps', [])
                    ]
                )

            alternatives = []
            for alt_data in data.get('alternatives', []):
                alternatives.append(ThoughtPath(
                    summary=alt_data.get('summary', ''),
                    doctrinal_fidelity=alt_data.get('doctrinal_fidelity', 0.0),
                    persuasive_effectiveness=alt_data.get('persuasive_effectiveness', 0.0),
                    confidence=alt_data.get('confidence', 0.0),
                    steps=[
                        ThoughtStep(
                            type=ThoughtStepType(step.get('type', 'strategic')),
                            content=step.get('content', '')
                        )
                        for step in alt_data.get('steps', [])
                    ]
                ))

            return ToTResponse(
                intention=data.get('intention', intention),
                paths_evaluated=data.get('paths_evaluated', 0),
                selected=selected,
                alternatives=alternatives,
                timestamp=data.get('timestamp', datetime.now().isoformat())
            )
        except Exception as error:
            print(f'[COGNITIVE CLIENT] Error in Tree of Thoughts: {error}')
            return None

    async def check_health(self) -> bool:
        """Verifica si el servicio cognitivo está disponible"""
        try:
            response = await self.client.get(f'{self.api_url}/health', timeout=5.0)
            return response.status_code == 200
        except:
            return False

    async def store_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Almacena conocimiento en el sistema cognitivo"""
        try:
            response = await self.client.post(
                f'{self.api_url}/knowledge/store',
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            print(f'[COGNITIVE CLIENT] Error storing knowledge: {error}')
            return {'success': False}

    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca conocimiento relacionado"""
        try:
            response = await self.client.get(
                f'{self.api_url}/knowledge/search',
                params={'query': query, 'limit': limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            print(f'[COGNITIVE CLIENT] Error searching knowledge: {error}')
            return []

    async def close(self) -> None:
        """Cierra el cliente HTTP"""
        await self.client.aclose()


# Instancia del cliente cognitivo
cognitive_client = CognitiveClient()
