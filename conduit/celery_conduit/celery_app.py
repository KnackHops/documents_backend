from celery import Celery


def create_celery(app):
    celery = Celery(
        app,
        broker=""
    )

    return celery


def init_celery(app):
    pass