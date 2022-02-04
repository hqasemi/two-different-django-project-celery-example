from typing import Any

from celery.result import AsyncResult
from django.db import models
from producer_django_project.celery import app

from celery import states as celery_result_states


class TaskModel(models.Model):
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(unique=True, max_length=100)
    is_revoked = models.BooleanField(default=False)

    @property
    def task_result(self) -> Any:
        """
        This is a model property, which is not being saved in db
        Everytime that a request reaches to this part of code,
        this field will be calculated using what has been saved in results_backend
        :return: result of this task if it was successful
        """

        # TODO: if a task is revoked and celery worker container
        #  is restarted, the task will be run and still its state
        #  will be `success`.
        if self.is_revoked or self.task_status == celery_result_states.REVOKED:
            # According to celery github repo (https://github.com/celery/celery/issues/4886)
            # celery does not support persistent revoke state in a db (like what is happening for
            # results using result_backend). So we make sure that when a task is flagged as
            # revoked, always the results will be None
            return None

        if self.task_status == celery_result_states.SUCCESS:
            # only if result stats is success, we return the result
            result = self.__task_result_instance.result
            return result

        return None

    @property
    def task_status(self) -> str:
        """
        This is a model property, which is not being saved in db
        Everytime that a request reaches to this part of code,
        this field will be calculated using what has been saved in results_backend
        :return: status of this task, e.g., success, failed, revoked, ...
        """
        return str(self.__task_result_instance.status)

    @property
    def __task_result_instance(self) -> AsyncResult:
        result = app.AsyncResult(self.task_id)
        return result
