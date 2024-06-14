import json
import logging
import jmespath
import requests

from django.core.cache import cache

from config.celery import app
from package.models import Package
from package.service import delivery_cost_calculation


logger = logging.getLogger('main')


@app.task
def calculate_delivery_cost_for_all_packages_task():
    usd_rate_in_rub = cache.get('usd_rate_in_rub')
    if usd_rate_in_rub is None:
        usd_rate_in_rub = update_usd_rate_in_rub_task()
    if usd_rate_in_rub is not None:
        packages = Package.objects.filter(delivery_cost__isnull=True)
        for package in packages:
            package.delivery_cost = delivery_cost_calculation(package.weight, package.cost_in_usd, usd_rate_in_rub)
        return Package.objects.bulk_update(packages, ['delivery_cost'])
    logger.warning('usd rate is None, delivery cost not calculated!')


@app.task
def update_usd_rate_in_rub_task():
    rates_url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    response = requests.get(rates_url)

    rates_data = json.loads(response.text)
    usd_rate_in_rub = jmespath.search('Valute.USD.Value', rates_data)
    if usd_rate_in_rub is not None:
        cache.set('usd_rate_in_rub', round(usd_rate_in_rub, 2))
        logger.info(f'usd_rate_in_rub was updated {usd_rate_in_rub}')
        return round(usd_rate_in_rub, 2)
    logger.warning('usd rate not found!')
