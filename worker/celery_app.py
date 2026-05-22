from celery import Celery
from apps.api.settings import get_settings

settings=get_settings()

celery_app=Celery(
    'prepared_worker',
    broker=settings.redis_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)
