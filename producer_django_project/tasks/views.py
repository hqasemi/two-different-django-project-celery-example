import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from producer_django_project.celery import app
from tasks.models import TaskModel
from tasks.serializers import TaskSerializer, TaskRevokeSerializer

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
    @swagger_auto_schema(
        request_body=TaskRevokeSerializer,
        responses={status.HTTP_200_OK: TaskSerializer()}
    )
    def revoke(self, request, *args, **kwargs):
        """ Revoke a task """
        task_instance: TaskModel = self.get_object()

        # we pass `is_revoked` as request.data, so that it could be validated in serializer
        # we also need to pass current instance to notify the serializer that
        # an instance is already existed, e.g., it is not a create request.
        request.data['is_revoked'] = True
        serializer = TaskRevokeSerializer(instance=task_instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        # revoke the celery task
        # app.control.revoke(task_instance.task_id, terminate=True, signal='SIGKILL')
        app.control.revoke(task_instance.task_id, terminate=True)

        # set is_revoked for this task
        serializer.save()

        # update task_instance object
        task_instance = self.get_object()
        response_serializer = self.serializer_class(instance=task_instance)

        return Response(response_serializer.data)
