import json
import logging
import jmespath
import requests

from django.core.cache import cache

from config.celery import app


logger = logging.getLogger('main')


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
