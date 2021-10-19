from conduit.app import celery


@celery.task()
def add_num(x, y):
    return x + y
