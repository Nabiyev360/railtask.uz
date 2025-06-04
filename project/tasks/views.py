import uuid
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from datetime import timedelta, date

from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from profiles.models import Profile
from django.http import JsonResponse, Http404
from django.utils.text import slugify
from django.core.files.base import ContentFile
from .models import Task, TaskComment, DeadlineExtensionRequest, TaskAnswerFile, TaskAnswer
from .services import to_latin, send_task_tg_users, tg_send_answer_assigner, tg_send_file_assigner



@login_required
def index_view(request):
    return redirect('/tasks/')


class TaskListView(LoginRequiredMixin, ListView):
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        tasks = Task.objects.filter(archived=False)

        if profile.role == "assigner":
            tasks = tasks.filter(author=profile)
        else:
            tasks = tasks.filter(performers=profile)

        expired_tasks = tasks.filter(deadline__lt=timezone.now()).exclude(status__in=['submitted', 'approved'])

        counts = {
            "all": tasks.count(),
            "expired": expired_tasks.count(),
            "in_progress": tasks.filter(status='in_progress').count(),
            "submitted": tasks.filter(status='submitted').count(),
            "approved": tasks.filter(status='approved').count(),

            "info": tasks.filter(degree='info').count(),
            "medium": tasks.filter(degree='medium').count(),
            "important": tasks.filter(degree='important').count(),
            "very_important": tasks.filter(degree='very_important').count(),
            "urgent": tasks.filter(degree='urgent').count(),
        }

        workers = Profile.objects.all().exclude(role="assigner")
        workers_task_count = {}
        for worker in workers:
            workers_task_count[worker] = tasks.filter(performers=worker).count()

        workers_task_count = dict(sorted(workers_task_count.items(), key=lambda item: item[1], reverse=True))   # sort by task count

        status = request.GET.get('status')
        degree = request.GET.get('degree')
        worker_id = request.GET.get('worker_id')
        if status == 'expired':
            tasks = expired_tasks
        elif status in ['in_progress', 'submitted', 'approved']:
            tasks = tasks.filter(status=status)
        elif degree:
            tasks = tasks.filter(degree=degree)
        elif worker_id:
            worker = Profile.objects.get(id=worker_id)
            tasks = tasks.filter(performers=worker)

        grouped_tasks = {}
        for task in tasks.order_by('deadline'):
            if task.deadline.date() == today:
                key = 'Bugun'
            elif task.deadline.date() == tomorrow:
                key = 'Ertaga'
            elif task.deadline:
                key = task.deadline.strftime('%d.%m.%Y')
            else:
                key = 'Muddatsiz'
            grouped_tasks.setdefault(key, []).append(task)

        performers = Profile.objects.exclude(role='assigner')

        return render(request, 'tasks/tasks.html', {
            'grouped_tasks': grouped_tasks,
            'performers': performers,
            'expired_tasks': expired_tasks,
            'counts': counts,
            'workers_task_count': workers_task_count,
        })



@csrf_exempt
def create_task_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = datetime.fromisoformat(request.POST.get('deadline'))
        degree = request.POST.get('degree')
        performer_ids = request.POST.getlist('performers')
        author = request.user.profile

        task = Task.objects.create(
            author=author,
            title=title,
            description=description,
            status='in_progress',
            deadline=deadline or None,
            degree=degree or None,
        )

        if performer_ids:
            performers = Profile.objects.filter(id__in=performer_ids)
            task.performers.set(performers)
            messages.success(request, 'Topshiriq muvaffaqiyatli yaratildi!')
            send_task_tg_users(task)
    return redirect('/tasks/')


def delete_task_veiw(request, task_id):
    task = Task.objects.get(id=task_id)
    task.archived = True
    task.save()
    return redirect('/tasks/')


def task_comment_view(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        TaskComment.objects.create(
            author=request.user.profile,
            task=task,
            comment=comment)
    return redirect('/tasks/')


def update_status_view(request, task_id):
    task = Task.objects.get(id=task_id)
    # if task.status == 'submitted':
    #     task.status = 'in_progress'
    # else:
    task.status = request.GET.get('status')
    task.save()
    return JsonResponse({'status': task.status})


def task_detail_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        raise Http404("Topshiriq topilmadi")

    return JsonResponse({
        'title': task.title,
        'description': task.description,
        'deadline': task.deadline.strftime('%Y-%m-%dT%H:%M'),
        'degree': task.degree,
        'performers': list(task.performers.values_list('id', flat=True)),
    })

def edit_task_view(request, task_id):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = datetime.fromisoformat(request.POST.get('deadline'))
        degree = request.POST.get('degree')
        performer_ids = request.POST.getlist('performers')

        task = Task.objects.get(id=task_id)
        task.title = title
        task.description = description
        task.deadline = deadline
        task.degree = degree
        task.performers.set(performer_ids)
        task.save()
        send_task_tg_users(task)
    return redirect('tasks:task_list')


@csrf_exempt
def request_deadline_view(request, task_id):
    task = Task.objects.get(id=task_id)
    requester = request.user.profile
    requested_deadline = datetime.fromisoformat(request.POST.get('requested_deadline'))
    reason = request.POST.get('reason')
    DeadlineExtensionRequest.objects.create(
        task = task,
        requester = requester,
        requested_deadline = requested_deadline,
        reason = reason
    )
    return redirect('tasks:task_list')


def extension_detail_view(request, extension_id):
    extension_request = DeadlineExtensionRequest.objects.get(id=extension_id)
    return JsonResponse({
        'der_deadline': extension_request.requested_deadline.strftime('%Y-%m-%dT%H:%M'),
        'der_reason': extension_request.reason,
    })

@csrf_exempt
def approve_deadline_view(request, extension_id):
    extension_request = DeadlineExtensionRequest.objects.get(id=extension_id)
    extension_request.responder = request.user.profile
    extension_request.status = 'approved'
    extension_request.accepted_deadline = request.POST.get('new_deadline')
    extension_request.responded_at = datetime.now()
    extension_request.save()
    task = extension_request.task
    task.deadline = datetime.fromisoformat(request.POST.get('new_deadline'))
    task.save()

    return redirect('tasks:task_list')


def reject_deadline_view(request, extension_id):
    extension_request = DeadlineExtensionRequest.objects.get(id=extension_id)
    extension_request.responder = request.user.profile
    extension_request.status = 'rejected'
    extension_request.is_read = False
    extension_request.responded_at = datetime.now()
    extension_request.save()
    return redirect('tasks:task_list')


def set_expired_tasks():
    expired_tasks = Task.objects.filter(deadline__lt=timezone.now()).exclude(status__in=['approved', 'submitted'])
    for task in expired_tasks:
        task.status = 'expired'
        task.save()


def dashboard_view(request):
    """Hozircha faqat oxirgi 30 kun uchun"""
    today = timezone.now()
    one_month_ago = today - relativedelta(months=1)
    tasks = Task.objects.filter(author__department=request.user.profile.department,
                                archived=False, deadline__range=(one_month_ago, today))
    todays_tasks = tasks.filter(deadline__date=date.today())
    todays_approved_tasks = tasks.filter(deadline__date=date.today(), status='approved')
    in_progress_tasks = tasks.filter(status='in_progress')
    approved_tasks = Task.objects.filter(status='approved')
    set_expired_tasks()
    expired_tasks = tasks.filter(status='expired')
    performers = Profile.objects.filter(department=request.user.profile.department).exclude(id=request.user.profile.id)

    for performer in performers:
        total = Task.objects.filter(performers=performer, deadline__range=(one_month_ago, today)).count()
        approved = Task.objects.filter(performers=performer, status='approved', deadline__range=(one_month_ago, today)).count()
        performer.task_completion_rate = round((approved / total) * 100, 1) if total > 0 else 0
        performer.total_tasks = total
        performer.approved_tasks = approved


    context = {
        "department_tasks": tasks,
        "todays_tasks": todays_tasks,
        "in_progress_tasks": in_progress_tasks,
        "approved_tasks": approved_tasks,
        "expired_tasks": expired_tasks,
        "todays_approved_tasks": todays_approved_tasks,
        "performers": performers,
    }

    return render(request, 'tasks/dashboard.html', context)


def calendar_tasks_view(request):
    tasks = Task.objects.filter(status__in=['in_progress', 'expired'], archived=False)
    events = []

    for task in tasks:
        events.append({
            "startDate": task.created_at.strftime('%Y-%m-%d'),  # yoki task.deadline uchun
            "endDate": task.deadline.strftime('%Y-%m-%dT%H:%M:%S'),
            "summary": task.title,
        })

    return JsonResponse(events, safe=False)


def answer_task_view(request, task_id):
    task = Task.objects.get(id=task_id)
    text = request.POST.get('answer_text')
    performer = request.user.profile
    TaskAnswer.objects.create(
        task = task,
        performer = performer,
        text = text,
    )
    task.status = 'submitted'
    task.save()
    tg_send_answer_assigner(task, performer, text)
    return redirect('tasks:task_list')



@csrf_exempt
def upload_file_view(request, task_id):
    if request.method == 'POST':
        task = Task.objects.get(id=task_id)
        file = request.FILES.get('filepond')
        performer = request.user.profile

        # --- Fayl nomini xavfsiz formatga o‘zgartirish ---
        original_name = file.name
        safe_filename = to_latin(original_name).replace('ы', '_')
        cleaned_file = ContentFile(file.read())
        cleaned_file.name = safe_filename

        # Faylni saqlash
        new_file = TaskAnswerFile.objects.create(
            task=task,
            performer=performer,
            file=cleaned_file
        )

        # Statusni o‘zgartirish
        task.status = 'submitted'
        task.save()

        # Telegramga yuborish
        tg_send_file_assigner(task, performer, new_file.file)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})
