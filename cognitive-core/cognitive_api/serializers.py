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
