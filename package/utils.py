from django.core.cache import cache

from package.tasks import update_usd_rate_in_rub_task


def get_usd_rate():
    rate = cache.get('usd_rate_in_rub')
    if rate is None:
        rate = update_usd_rate_in_rub_task()
    return rate
