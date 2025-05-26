from django.contrib import admin

from .models import Task, TaskComment, DeadlineExtensionRequest, TaskAnswer, TaskAnswerFile


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'status')
    search_fields = ('id', 'title', 'description')
    list_display_links = ('id', 'title')

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'comment')
    search_fields = ('task', 'comment')

@admin.register(DeadlineExtensionRequest)
class DeadlineExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ('reason', 'requested_deadline', 'accepted_deadline')
    search_fields = ('reason', 'requested_deadline', 'accepted_deadline')

@admin.register(TaskAnswer)
class TaskAnswerAdmin(admin.ModelAdmin):
    list_display = ('task__title', 'text')
    search_fields = ('task__title', 'text')

@admin.register(TaskAnswerFile)
class TaskAnswerFileAdmin(admin.ModelAdmin):
    list_display = ('task', 'file', 'performer')
    search_fields = ('task', 'file', 'performer')