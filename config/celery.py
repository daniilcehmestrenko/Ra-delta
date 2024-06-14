import os
from datetime import timedelta
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'update-rub-rate-every-5-minute': {
        'task': 'package.tasks.update_usd_rate_in_rub_task',
        'schedule': timedelta(minutes=5),
    },
    'update-delivery-cost-for-all-packages-where-delivery-cost-is-null-every-5-min': {
        'task': 'package.tasks.calculate_delivery_cost_for_all_packages_task',
        'schedule': timedelta(minutes=5),
    },
}
app.conf.timezone = 'UTC'
app.autodiscover_tasks()
