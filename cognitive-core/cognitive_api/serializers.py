"""
Serializers Django REST Framework para Cognitive Core
"""

from rest_framework import serializers
from typing import Dict, Any


class CognitiveRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes cognitivas"""
    intention = serializers.CharField(max_length=1000)
    context = serializers.DictField(child=serializers.CharField(), required=False)
    urgency = serializers.ChoiceField(choices=['low', 'medium', 'high'], default='medium')
    metadata = serializers.DictField(child=serializers.CharField(), required=False)


class CognitiveResponseSerializer(serializers.Serializer):
    """Serializer para respuestas cognitivas"""
    decision = serializers.CharField()
    reasoning = serializers.CharField()
    confidence = serializers.FloatField()
    requires_human_approval = serializers.BooleanField()
    related_concepts = serializers.ListField(child=serializers.CharField())
    risk_level = serializers.ChoiceField(choices=['low', 'medium', 'high'])
    timestamp = serializers.CharField()
    mode = serializers.CharField()


class KnowledgeStoreSerializer(serializers.Serializer):
    """Serializer para almacenamiento de conocimiento"""
    content = serializers.CharField()
    type = serializers.CharField()
    metadata = serializers.DictField(child=serializers.CharField(), required=False)


class ToTRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes Tree of Thoughts"""
    intention = serializers.CharField(max_length=1000)
    context = serializers.DictField(child=serializers.CharField(), required=False)


class AutonomousStartRequestSerializer(serializers.Serializer):
    """Serializer para iniciar sistema autónomo"""
    controller_id = serializers.CharField(max_length=100)


class AutonomousActionRequestSerializer(serializers.Serializer):
    """Serializer para procesar solicitud autónoma"""
    type = serializers.CharField(max_length=100)
    data = serializers.DictField(child=serializers.CharField())
    urgency = serializers.ChoiceField(choices=['low', 'medium', 'high'], default='medium')


class ApprovalRequestSerializer(serializers.Serializer):
    """Serializer para aprobación de acciones"""
    action_id = serializers.CharField(max_length=100)
    controller_id = serializers.CharField(max_length=100)


class NeuroSymbolicTaskSerializer(serializers.Serializer):
    """Serializer para tareas neuro-simbólicas"""
    task = serializers.CharField(max_length=200)
    input_data = serializers.JSONField()
    paradigms = serializers.ListField(child=serializers.CharField(), required=False)


class DomainKnowledgeSerializer(serializers.Serializer):
    """Serializer para conocimiento de dominio"""
    facts = serializers.ListField(child=serializers.CharField(), required=False)
    patterns = serializers.ListField(child=serializers.JSONField(), required=False)


class ConsciousnessControlSerializer(serializers.Serializer):
    """Serializer para control de conciencia"""
    command = serializers.ChoiceField(choices=['awaken', 'sleep', 'focus', 'meditate'])
    parameter = serializers.CharField(required=False, allow_blank=True)


class ChatMessageSerializer(serializers.Serializer):
    """Serializer para mensajes de chat"""
    message = serializers.CharField(max_length=2000)
    user_id = serializers.CharField(required=False, allow_blank=True)
    context = serializers.DictField(child=serializers.CharField(), required=False)


class PlanSerializer(serializers.Serializer):
    """Serializer para crear un plan soberano"""
    user_id = serializers.CharField()
    nombre = serializers.CharField()
    proposito = serializers.CharField()


class PlanNodeSerializer(serializers.Serializer):
    """Serializer para agregar nodos a un plan"""
    plan_id = serializers.CharField(required=False, allow_blank=True)
    fase_id = serializers.CharField(required=False, allow_blank=True)
    action_id = serializers.CharField(required=False, allow_blank=True)
    descripcion = serializers.CharField()
    prioridad = serializers.FloatField(required=False, default=0.5)
    criterio_exito = serializers.CharField(required=False, allow_blank=True)
    orden = serializers.IntegerField(required=False, default=1)
    estado = serializers.CharField(required=False, allow_blank=True)
    probabilidad = serializers.FloatField(required=False, default=0.5)
    impacto = serializers.FloatField(required=False, default=0.5)


class MutatePlanSerializer(serializers.Serializer):
    """Serializer para mutar un plan (refutar accion, cambiar estado)"""
    action_id = serializers.CharField()
    new_status = serializers.CharField(required=False, allow_blank=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    new_action_description = serializers.CharField(required=False, allow_blank=True)


class SemanticShadowSerializer(serializers.Serializer):
    """Serializer para guardar sombra semantica"""
    plan_id = serializers.CharField()
    user_id = serializers.CharField()
    content = serializers.CharField()
    content_type = serializers.CharField(required=False, default="plan_summary")
