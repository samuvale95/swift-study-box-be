"""
Celery configuration for background tasks
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery = Celery(
    "swift_study_box",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.file_processing",
        "app.tasks.ai_processing",
        "app.tasks.notifications"
    ]
)

# Configure Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
