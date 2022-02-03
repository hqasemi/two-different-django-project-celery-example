import logging

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from producer_django_project.celery import app
from tasks.models import TaskModel
from tasks.serializers import TaskSerializer

logger = logging.getLogger(__name__)


class TasksModelViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """
    This view creates all the required methods for list, create, and retrieve automatically.

    please have a look at this link: https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/

    """
    queryset = TaskModel.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'task_id'

    def create(self, request, *args, **kwargs):
        """ Creates a new task

        - Create a new task in DB.
        """
        task_name = request.data.get('task_name')
        res = app.send_task(task_name, args=[1, 2, ])

        task_id = res.id
        request.data['task_id'] = task_id

        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """ Lists all the available tasks

        - Show all the tasks and their details together.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """ Retrieve an task based on its database ID

        - Show all the task and their details together.
        """
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["POST"], url_path="revoke", url_name=None)
    def soft_delete(self, request, *args, **kwargs):
        """ Revoke a task """
        task: TaskModel = self.get_object()
        if task.is_revoked:
            return Response(status=status.HTTP_200_OK, data="The task has been already revoked")

        task.is_revoked = True
        task.save()
        return Response(status=status.HTTP_200_OK, data="The task is now revoked")
