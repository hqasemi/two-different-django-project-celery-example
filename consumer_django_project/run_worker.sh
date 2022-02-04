# persistent revokes: https://docs.celeryproject.org/en/latest/userguide/workers.html#worker-persistent-revokes
celery -A consumer_django_project worker -l info --statedb=/var/run/celery/worker-$(hostname).state
