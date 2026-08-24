from django.urls import path
from . import views

urlpatterns = [
    path('', views.core, name='core'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    # URL route for clearing completed tasks
    path('clear-completed/', views.clear_completed, name='clear_completed'),
    # URL route for editing a task
    path('edit/<int:task_id>/', views.edit_task, name='edit_task'),
]