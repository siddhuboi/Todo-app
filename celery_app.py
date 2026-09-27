from celery import Celery

celery = Celery(
    "todo_app",
    broker="redis://localhost:6379/0",
    include=["celery_tasks"]
)