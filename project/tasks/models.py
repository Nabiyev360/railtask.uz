import os
from django.db import models

from profiles.models import Profile


class Task(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Topshiriq berildi'),
        ('accepted', 'Qabul qilindi'),
        ('in_progress', 'Bajarilmoqda'),
        ('submitted', 'Tasdiqlashga yuborilgan'),
        ('approved', 'Tasdiqlandi'),
        ('expired', 'Bajarilmadi'),
        ('returned', 'Qayta ishlashga yuborildi'),
    ]

    DEGREE_CHOICES = [
        ('info', "Ma'lumot uchun"),
        ('medium', "Ahamiyatli"),
        ('important', "Muhim"),
        ('very_important', "Juda muhim"),
        ('urgent', "Tezkor"),
    ]

    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='author')
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    performers = models.ManyToManyField(Profile, related_name='performers')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    received = models.DateField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, default='medium')
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TaskAnswer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='answers')
    performer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class TaskAnswerFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    performer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/answer_files')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class TaskComment(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.comment


class DeadlineExtensionRequest(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'Jarayonda'),
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Bekor qilindi')
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='deadline_extension_requests')
    requester = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='deadline_requests_made')
    responder = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='deadline_requests_responded')
    reason = models.TextField(null=True, blank=True)
    requested_deadline = models.DateTimeField(null=True, blank=True)
    accepted_deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='in_progress')
    is_read = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.requester} requested extension for Task #{self.task.id}"

