from django.utils import timezone

from tasks.models import DeadlineExtensionRequest, Task


def deadline_extension_requests(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'assigner':
            workers = request.user.profile.department.profiles.all()
            deadline_ext_requests = DeadlineExtensionRequest.objects.filter(requester__in=workers, status='in_progress')
        elif request.user.profile.role == 'performer':
            deadline_ext_requests = DeadlineExtensionRequest.objects.filter(requester=request.user.profile, is_read=False,
                                                                            task__status='in_progress')
        else:
            deadline_ext_requests = []
        return {'deadline_ext_requests': deadline_ext_requests}
    return {}


def expired_tasks_notification(request):
    if request.user.is_authenticated:
        expired_tasks = Task.objects.filter(deadline__lt=timezone.now()).exclude(status__in=['completed', 'approved'])
        return {'expired_tasks': expired_tasks}
    return {}

