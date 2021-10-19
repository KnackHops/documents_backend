import os

from celery import Celery


def create_celery(app_name):
    celery_broker = os.environ.get('CELERY_BROKER_URL')
    celery_backend = os.environ.get('CELERY_BACKEND_URL')

    return Celery(app_name, broker=celery_broker, backend=celery_backend, include=['conduit.views.celery_task'])


def init_celery(celery, app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

