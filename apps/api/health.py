from fastapi import APIRouter
from sqlalchemy import text
from .database import SessionLocal

router=APIRouter(prefix='/health',tags=['health'])

@router.get('/db')
def database_health():
    try:
        with SessionLocal() as db:
            db.execute(text('SELECT 1'))
        return {'status':'ok','database':'reachable'}
    except Exception as exc:
        return {'status':'error','database':'unreachable','detail':str(exc)}
