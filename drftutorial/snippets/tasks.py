import logging

from django.db import connection

from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(autoretry_for=(Exception,), max_retries=3, retry_backoff=3)
def remove_expired_snippets():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM snippet WHERE expired_at IS NOT NULL AND expired_at <= NOW()')
