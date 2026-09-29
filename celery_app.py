from celery import Celery

celery = Celery(
    "todo_app",
    broker="redis://redis:6379/0",
    include=["celery_tasks"]
)