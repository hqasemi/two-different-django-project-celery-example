import logging
import os
import time

from celery import Celery

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'consumer_django_project.settings')

app = Celery('proj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(name='sum', bind=True)
def sum_task(self, a: float, b: float) -> float:
    """ A sample task which can be run in another
    process (microservice) using its name (here 'sum')
    """
    task_name = self.name
    logger.info(f"Task named '{task_name}' is being run "
                f"using arguments: '{a}' and '{b}'")
    # We use 10 seconds delay just to simulate a task which takes some time to be done
    time.sleep(10)

    return a + b
