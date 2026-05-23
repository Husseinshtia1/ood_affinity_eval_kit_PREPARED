from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import get_settings
from .jobs import router as jobs_router
from .health import router as health_router

settings=get_settings()
app=FastAPI(title=settings.app_name,version=settings.app_version)

app.add_middleware(
CORSMiddleware,
allow_origins=settings.allowed_origins,
allow_credentials=True,
allow_methods=['*'],
allow_headers=['*']
)

app.include_router(jobs_router)
app.include_router(health_router)

@app.get('/health')
def health():
 return {
   'status':'ok',
   'service':'prepared-api',
   'version':settings.app_version
 }
