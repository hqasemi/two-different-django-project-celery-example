from typing import Any

from celery.result import AsyncResult
from django.db import models
from django.utils.translation import gettext_lazy as _

from producer_django_project.celery import app


class TaskResultStatusChoices(models.TextChoices):
    PENDING = "PENDING", _("PENDING")
    STARTED = "STARTED", _("STARTED")
    RETRY = "RETRY", _("RETRY")
    FAILURE = "FAILURE", _("FAILURE")
    SUCCESS = "SUCCESS", _("SUCCESS")


class TaskModel(models.Model):
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(unique=True, max_length=100)
    is_revoked = models.BooleanField(default=False)

    @property
    def task_result(self) -> Any:
        result = self.__task_result.result
        return result

    @property
    def task_status(self) -> TaskResultStatusChoices:
        return TaskResultStatusChoices(self.__task_result.status)

    @property
    def __task_result(self) -> AsyncResult:
        result = app.AsyncResult(self.task_id)
        return result
