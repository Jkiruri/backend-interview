import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')

app = Celery('orderflow')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery Configuration
app.conf.update(
    # Broker settings
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'notifications.tasks.send_sms_notification': {'queue': 'sms'},
        'notifications.tasks.send_email_notification': {'queue': 'email'},
        'notifications.tasks.send_order_confirmation': {'queue': 'notifications'},
        'notifications.tasks.send_order_status_update': {'queue': 'notifications'},
    },
    
    # Queue definitions
    task_default_queue='default',
    task_queues={
        'default': {
            'exchange': 'default',
            'routing_key': 'default',
        },
        'sms': {
            'exchange': 'notifications',
            'routing_key': 'sms',
        },
        'email': {
            'exchange': 'notifications',
            'routing_key': 'email',
        },
        'notifications': {
            'exchange': 'notifications',
            'routing_key': 'notifications',
        },
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Retry settings
    task_annotations={
        'notifications.tasks.send_sms_notification': {
            'rate_limit': '10/m',  # Max 10 SMS per minute
            'retry_backoff': True,
            'max_retries': 3,
        },
        'notifications.tasks.send_email_notification': {
            'rate_limit': '30/m',  # Max 30 emails per minute
            'retry_backoff': True,
            'max_retries': 3,
        },
    },
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

