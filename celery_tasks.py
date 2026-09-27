from celery_app import celery
from send_email import send_mail


@celery.task
def send_task_email(
    receiver_mail: str,
    subject: str,
    body: str
):
    send_mail(
        receiver_mail=receiver_mail,
        subject=subject,
        body=body
    )