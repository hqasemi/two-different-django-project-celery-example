from typing import Any

from celery import states as celery_result_states
from celery.result import AsyncResult
from django.db import models

from producer_django_project.celery import app


class TaskModel(models.Model):
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(unique=True, max_length=100)
    is_revoked = models.BooleanField(default=False)

    @property
    def task_result(self) -> Any:
        result = self.__get_task_result_instance().result
        if self.task_status == celery_result_states.SUCCESS:
            return result
        return None

    @property
    def task_status(self) -> str:
        return str(self.__get_task_result_instance().status)

    def __get_task_result_instance(self) -> AsyncResult:
        result = app.AsyncResult(self.task_id)
        return result
