import time
import random
import os

from celery import Celery

broker_host = os.environ['BROKER_HOST']
broker_user = os.environ['BROKER_USER']
broker_password = os.environ['BROKER_PASSWORD']
broker_vhost = os.environ['BROKER_VHOST']

broker_config = 'amqp://' + broker_user + ':' + broker_password + '@' + broker_host + '/' + broker_vhost
result_config = 'rpc://'

celery = Celery('nlp_service', broker=broker_config, backend=result_config)


@celery.task(bind=True, name='long_task')
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verbs = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjectives = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    nouns = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']

    message = ''

    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verbs),
                                              random.choice(adjectives),
                                              random.choice(nouns))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total, 'status': message})

        time.sleep(1)

    return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42}
