from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Account(models.Model):
    username = models.CharField(max_length=20, unique=True, primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    YEAR_CHOICES = (
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
        ('4', 'Fourth'),
    )
    year = models.CharField(max_length=20, choices=YEAR_CHOICES, default=1)
    major = models.CharField(max_length=100)
    minor = models.CharField(max_length=100)
    courses = models.ManyToManyField("Course", blank=True)
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)

    def __str__(self):
        return self.username


class Course(models.Model):
    name = models.CharField(max_length=200, default='', unique=True, primary_key=True)
    department = models.CharField(max_length=4, default='')
    number = models.CharField(max_length=4, default='')
    professor = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.name


class StudySession(models.Model):
    topic = models.CharField(max_length=50, default='Study Session', unique=True)
    members = models.ManyToManyField("Account", blank=True, related_name="study_sessions")
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.localtime)
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="study_sessions"
    )

    def __str__(self):
        return self.topic


class ThreadModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    has_unread = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + " to " + self.receiver.username


class MessageModel(models.Model):
    thread = models.ForeignKey('ThreadModel', related_name='+', on_delete=models.CASCADE, blank=True, null=True)
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    body = models.CharField(max_length=1000)
    # image = models.ImageField(upload_to='', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return "'" + self.body + "'" + " from " + self.sender_user.username + " to " + self.receiver_user.username
