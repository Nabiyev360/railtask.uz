from django.urls import path

from .views import (TaskListView, create_task_view, delete_task_veiw, task_comment_view, update_status_view,
                    task_detail_view, edit_task_view, request_deadline_view, extension_detail_view,
                    approve_deadline_view,
                    reject_deadline_view, dashboard_view, calendar_tasks_view, answer_task_view, upload_file_view)

app_name = 'tasks'


urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('<int:task_id>/', task_detail_view, name='task_detail'),
    path('create', create_task_view, name='create_task'),
    path('edit/<int:task_id>', edit_task_view, name='edit'),
    path('delete/<int:task_id>', delete_task_veiw, name='delete_task'),
    path('update-status/<int:task_id>', update_status_view, name='update_status'),
    path('task-comment/<int:task_id>', task_comment_view, name='task_comment'),
    path('answer-task/<int:task_id>', answer_task_view, name='answer_task'),
    path('upload-file/<int:task_id>', upload_file_view, name='upload_file'),

    path('<int:task_id>/extend', request_deadline_view, name='request_deadline'),
    path('extensions/<int:extension_id>', extension_detail_view, name='extension_detail'),
    path('extensions/<int:extension_id>/approve', approve_deadline_view, name='approve_extension'),
    path('extensions/<int:extension_id>/reject', reject_deadline_view, name='reject_extension'),

    path('dashboard', dashboard_view, name='dashboard'),
    path('calendar-tasks', calendar_tasks_view, name='calendar_tasks'),
]
