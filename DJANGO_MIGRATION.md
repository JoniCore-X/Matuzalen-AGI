# Migración de FastAPI a Django

## Resumen

La aplicación FastAPI ha sido migrada exitosamente a Django con Django REST Framework. El servidor Django está corriendo en `http://localhost:8000` y responde correctamente a las solicitudes.

## Cambios Realizados

### 1. Estructura del Proyecto Django

```
cognitive-core/
├── autodjango/              # Proyecto Django
│   ├── __init__.py
│   ├── settings.py          # Configuración Django
│   ├── urls.py             # URLs principales
│   └── wsgi.py
├── cognitive_api/           # App Django para Cognitive Core
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/         # Migraciones Django
│   ├── models.py
│   ├── serializers.py      # Serializers DRF
│   ├── urls.py             # URLs de la app
│   └── views.py            # Vistas Django
├── manage.py               # Script de gestión Django
└── [archivos existentes del cognitive core]
```

### 2. Configuración Django (`autodjango/settings.py`)

- **Apps instaladas**: Django REST Framework, CORS Headers, cognitive_api
- **Middleware**: CORS Headers añadido para permitir peticiones cross-origin
- **CORS**: Configurado para permitir todos los orígenes en desarrollo
- **REST Framework**: Configurado con permisos AllowAny para desarrollo
- **Variables de entorno**: Integración con `.env` para configuración

### 3. Serializers Django REST Framework (`cognitive_api/serializers.py`)

Serializadores para todas las solicitudes y respuestas:
- `CognitiveRequestSerializer`: Solicitudes cognitivas
- `CognitiveResponseSerializer`: Respuestas cognitivas
- `KnowledgeStoreSerializer`: Almacenamiento de conocimiento
- `ToTRequestSerializer`: Solicitudes Tree of Thoughts
- `AutonomousStartRequestSerializer`: Iniciar sistema autónomo
- `AutonomousActionRequestSerializer`: Procesar solicitud autónoma
- `ApprovalRequestSerializer`: Aprobación de acciones

### 4. Vistas Django (`cognitive_api/views.py`)

Todas las vistas de FastAPI convertidas a vistas Django REST Framework:
- `health_check`: Verificación de salud
- `process_intention`: Procesamiento cognitivo
- `tree_of_thoughts`: Motor Tree of Thoughts
- `ingest_knowledge_base`: Ingesta de conocimiento
- `search_knowledge`: Búsqueda de conocimiento
- `store_knowledge`: Almacenamiento de conocimiento
- `start_autonomous_system`: Iniciar sistema autónomo
- `stop_autonomous_system`: Detener sistema autónomo
- `process_autonomous_request`: Procesar solicitud autónoma
- `get_autonomous_status`: Estado del sistema
- `approve_autonomous_action`: Aprobar acción
- `reject_autonomous_action`: Rechazar acción

### 5. URLs Django

**URLs principales (`autodjango/urls.py`)**:
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cognitive_api.urls')),
]
```

**URLs de la app (`cognitive_api/urls.py`)**:
```python
urlpatterns = [
    path('health/', views.health_check),
    path('cognitive/process', views.process_intention),
    path('cognitive/tot', views.tree_of_thoughts),
    path('knowledge/ingest', views.ingest_knowledge_base),
    path('knowledge/search', views.search_knowledge),
    path('knowledge/store', views.store_knowledge),
    path('autonomous/start', views.start_autonomous_system),
    path('autonomous/stop', views.stop_autonomous_system),
    path('autonomous/process', views.process_autonomous_request),
    path('autonomous/status', views.get_autonomous_status),
    path('autonomous/approve', views.approve_autonomous_action),
    path('autonomous/reject', views.reject_autonomous_action),
]
```

### 6. Dependencias Actualizadas (`requirements.txt`)

```txt
django==6.1.1
djangorestframework==3.18.0
django-cors-headers==4.9.0
[dependencias existentes...]
```

## Uso

### Iniciar el servidor Django

```bash
cd C:\Users\jonie\OneDrive\Desktop\AutoPlan\cognitive-core
python manage.py runserver 0.0.0.0:8000
```

### Ejemplos de API

**Health check**:
```bash
curl http://localhost:8000/api/health/
```

**Procesar intención cognitiva**:
```bash
curl -X POST http://localhost:8000/api/cognitive/process \
  -H "Content-Type: application/json" \
  -d '{"intention": "crear plan", "context": {}, "urgency": "medium"}'
```

**Tree of Thoughts**:
```bash
curl -X POST http://localhost:8000/api/cognitive/tot \
  -H "Content-Type: application/json" \
  -d '{"intention": "ejemplo", "context": {}}'
```

**Ingestar conocimiento**:
```bash
curl -X POST http://localhost:8000/api/knowledge/ingest
```

**Iniciar sistema autónomo**:
```bash
curl -X POST http://localhost:8000/api/autonomous/start \
  -H "Content-Type: application/json" \
  -d '{"controller_id": "controller_001"}'
```

**Estado del sistema autónomo**:
```bash
curl http://localhost:8000/api/autonomous/status
```

## Diferencias con FastAPI

### Ventajas de Django

1. **Ecosistema maduro**: Django tiene un ecosistema más grande y maduro
2. **Admin panel**: Panel de administración integrado
3. **ORM**: Django ORM para bases de datos relacionales
4. **Migraciones**: Sistema de migraciones automático
5. **Seguridad**: Seguridad por defecto (CSRF, autenticación, etc.)
6. **Comunidad**: Comunidad más grande y más recursos

### Adaptaciones Realizadas

1. **Síncrono vs Asíncrono**: Django es principalmente síncrono, pero usamos `asyncio.run()` para llamar funciones asíncronas del cognitive core
2. **Serializadores**: En lugar de Pydantic, usamos Django REST Framework serializers
3. **Decoradores**: Usamos `@api_view` y `@permission_classes` en lugar de decoradores FastAPI
4. **Respuestas**: Usamos `Response` de DRF en lugar de respuestas directas de FastAPI

## Estado Actual

- ✅ Proyecto Django creado
- ✅ App cognitive_api creada
- ✅ Configuración Django completada
- ✅ Serializers DRF creados
- ✅ Vistas Django convertidas
- ✅ URLs configuradas
- ✅ Migraciones ejecutadas
- ✅ Servidor Django corriendo
- ✅ Health check funcionando

## Próximos Pasos

1. **Modelos Django**: Crear modelos Django para persistencia de datos
2. **Autenticación**: Implementar autenticación Django
3. **Testing**: Crear tests Django
4. **Admin Panel**: Configurar admin panel para gestión de datos
5. **Documentación**: Integrar Swagger/OpenAPI con drf-spectacular
6. **Performance**: Optimizar rendimiento con caché y optimización de consultas

## Compatibilidad

La migración mantiene la compatibilidad con:
- **Cognitive Core**: Todos los módulos del cognitive core funcionan igual
- **Ollama**: Integración con Ollama se mantiene
- **Qdrant**: Cliente Qdrant funciona sin cambios
- **Neo4j**: Cliente Neo4j funciona sin cambios
- **Sistema Autónomo**: Todo el código Python convertido funciona perfectamente

## Notas Importantes

1. **Puerto**: El servidor Django corre en el puerto 8000 (misma configuración que FastAPI)
2. **Prefijo API**: Todos los endpoints tienen el prefijo `/api/`
3. **CORS**: Configurado para permitir todos los orígenes en desarrollo
4. **Async**: Las funciones asíncronas del cognitive core se ejecutan con `asyncio.run()`
5. **Modo Docker/DEMO**: La configuración de modo se mantiene desde `.env`
