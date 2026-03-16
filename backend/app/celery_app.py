from celery import Celery
from app.config import settings

celery_app = Celery(
    "docagent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.document_tasks"]
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=settings.celery_task_time_limit,
    task_ignore_result=False,
    result_expires=3600,
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
)
