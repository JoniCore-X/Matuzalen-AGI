from app.api.v1.router import router as api_v1_router
from app.config.settings import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version='0.1.0',
    description='PlanBot backend API',
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_v1_router)


@app.get('/health')
def health_check():
    return {'status': 'ok', 'app': settings.app_name, 'env': settings.env}


@app.get('/')
def root():
    return {'message': 'PlanBot API is running'}
