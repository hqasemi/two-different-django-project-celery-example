from django.urls import path

from tasks.views import run_task_sum_view

urlpatterns = [
    path('run/', run_task_sum_view),
]
