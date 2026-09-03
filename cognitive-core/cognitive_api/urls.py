"""
URL Configuration para Cognitive API
"""

from django.urls import path
from . import views

urlpatterns = [
    # API root
    path('', views.api_root, name='api_root'),

    # Health check
    path('health/', views.health_check, name='health_check'),

    # Cognitive processing
    path('cognitive/process', views.process_intention, name='process_intention'),
    path('cognitive/tot', views.tree_of_thoughts, name='tree_of_thoughts'),

    # Knowledge management
    path('knowledge/ingest', views.ingest_knowledge_base, name='ingest_knowledge_base'),
    path('knowledge/search', views.search_knowledge, name='search_knowledge'),
    path('knowledge/store', views.store_knowledge, name='store_knowledge'),

    # Autonomous system
    path('autonomous/start', views.start_autonomous_system, name='start_autonomous_system'),
    path('autonomous/stop', views.stop_autonomous_system, name='stop_autonomous_system'),
    path('autonomous/process', views.process_autonomous_request, name='process_autonomous_request'),
    path('autonomous/status', views.get_autonomous_status, name='get_autonomous_status'),
    path('autonomous/approve', views.approve_autonomous_action, name='approve_autonomous_action'),
    path('autonomous/reject', views.reject_autonomous_action, name='reject_autonomous_action'),

    # Neuro-symbolic system
    path('neuro-symbolic/process', views.process_neuro_symbolic_task, name='process_neuro_symbolic_task'),
    path('neuro-symbolic/status', views.get_neuro_symbolic_status, name='get_neuro_symbolic_status'),
    path('neuro-symbolic/knowledge', views.add_domain_knowledge, name='add_domain_knowledge'),
    path('neuro-symbolic/validate', views.validate_llm_output, name='validate_llm_output'),

    # Autonomous consciousness
    path('consciousness/control', views.control_consciousness, name='control_consciousness'),
    path('consciousness/state', views.get_consciousness_state, name='get_consciousness_state'),
    path('consciousness/interval', views.set_perception_interval, name='set_perception_interval'),

    # Chat with agent
    path('chat', views.chat_with_agent, name='chat_with_agent'),
    path('chat/simple', views.chat_simple, name='chat_simple'),
]
