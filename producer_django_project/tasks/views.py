from django.http import HttpResponse

from producer_django_project.celery import app


def run_task_view(request):
    app.send_task('task_1', args=["sample_arg", ])
    return HttpResponse(content=f"Task is run", status=200)
