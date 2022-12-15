import time

from celery import shared_task

from services.ses import SESservice
from watch_shop.auth_app.models import Profile
# celery -A watch_shop worker --loglevel=INFO -P gevent


@shared_task
def send_email_to_new_users(email):
    SESservice().send_email(email)


@shared_task
def send_email_when_checkout_invoked(email, order):
    SESservice().send_email(email, order)


@shared_task
def send_email_to_new_users123(pk):
    p = Profile.objects.get(user_id=pk)
    time.sleep(7)
    p.first_name = 'test'
    p.save()
    time.sleep(7)
    p.first_name = 'test2'
    p.save()
