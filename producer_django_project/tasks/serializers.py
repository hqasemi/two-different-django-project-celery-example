from rest_framework import serializers

from tasks.models import TaskModel


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        # fields = '__all__'
        # Because (task_result and task_status) are not a model fields,
        # it needs to add all the fields and properties explicitly to the serializer class
        fields = (
            "task_name",
            "task_id",
            "is_revoked",
            "task_result",
            "task_status",
        )
