import logging
from datetime import timedelta, datetime

from django.utils.translation import gettext_lazy as _
from producer_django_project.celery import app
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tasks.models import TaskModel

from celery import states as celery_result_states

logger = logging.getLogger(__name__)


class TaskSerializer(serializers.ModelSerializer):
    """ Base task serializer class which performs field validations """

    class Meta:
        model = TaskModel
        # fields = '__all__'
        # Because (`task_result` and `task_status`) are not a model fields,
        # it needs to add all the fields and properties explicitly to the serializer class
        fields = (
            "task_name",
            "task_id",
            "is_revoked",
            "task_result",
            "task_status",
        )

    task_id = serializers.ReadOnlyField()
    is_revoked = serializers.ReadOnlyField(required=False)

    def create(self, validated_data):
        task_name = validated_data.get('task_name')

        schedule_time = datetime.now() + timedelta(seconds=50)
        # we added `eta`, which leads the task to be run after 50 seconds
        res = app.send_task(task_name, args=[1, 2, ], eta=schedule_time)

        task_id = res.id
        validated_data['task_id'] = task_id

        return super().create(validated_data)


class TaskRevokeSerializer(TaskSerializer):
    class Meta:
        model = TaskModel

        # no field is needed to get involved in serializer
        # we just need this serializer to validate the is_revoked field
        # which is being set manually in view
        fields = (
            'is_revoked',
        )

    is_revoked = serializers.BooleanField()

    def validate_is_revoked(self, is_revoked: bool):
        if self.instance is None and is_revoked:
            raise ValidationError(
                _("is_revoked may not be set")
            )

        if self.instance.is_revoked and is_revoked:
            raise ValidationError(
                _("The task has been already revoked")
            )

        revoked_is_not_allowed_task_states = (
            celery_result_states.SUCCESS,
            celery_result_states.FAILURE,
        )

        if self.instance.task_status in revoked_is_not_allowed_task_states and is_revoked:
            raise ValidationError(
                _(f"Task with status '{self.instance.task_status}'"
                  f"is not allowed to get revoked")
            )

        if not is_revoked and self.instance.is_revoked and \
                self.instance.task_status not in revoked_is_not_allowed_task_states:
            raise ValidationError(
                _(f"Task with status '{self.instance.task_status}'"
                  f"is done, its `is_revoked` field cannot get unset anymore")
            )

        return is_revoked
