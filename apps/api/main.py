from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import get_settings
from .production_guard import assert_safe_production_config
from .jobs import router as jobs_router
from .health import router as health_router
from .auth import router as auth_router
from .auth_me import router as auth_me_router
from .audit_routes import router as audit_router
from .organization_routes import router as organization_router
from .invitation_routes import router as invitation_router

settings=get_settings()
assert_safe_production_config(settings)

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
app.include_router(auth_router)
app.include_router(auth_me_router)
app.include_router(audit_router)
app.include_router(organization_router)
app.include_router(invitation_router)

@app.get('/health')
def health():
 return {
   'status':'ok',
   'service':'prepared-api',
   'version':settings.app_version
 }
