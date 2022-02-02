import os

from celery import Celery

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


@app.task(name='task_1', bind=True)
def sample_task(self, arg1):
    """ A sample_task which can be run in another process (microservice)
    using its name (here 'task_1')"""
    # print(f'Request: {self.request!r}')
    output = f"Task1 is being run using argument: {arg1}"
    return output
