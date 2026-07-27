
from .celery import app as celery_app

__all__ = ('celery_app',)
# load celery app when django starts