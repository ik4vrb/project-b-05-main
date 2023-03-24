from django.contrib import admin
from .models import Account, StudySession, Course, ThreadModel, MessageModel


class StudySessionInline(admin.TabularInline):
    model = StudySession
    extra = 0


class StudySessionMembersInline(admin.TabularInline):
    model = StudySession.members.through
    extra = 0


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'professor')
    search_fields = ['name']
    inlines = [StudySessionInline]


class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'course', 'date', 'time')
    search_fields = ['topic']


class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', "year", 'major', 'minor')
    list_filter = ('major', 'minor', 'year')
    search_fields = ['username']
    inlines = [StudySessionMembersInline]


class ThreadAdmin(admin.ModelAdmin):
    search_fields = ['u\classesser']
    list_display = ('user', 'receiver')


class MessageAdmin(admin.ModelAdmin):
    search_fields = ['user']
    list_display = ('body', 'sender_user', 'receiver_user')


admin.site.register(Course, CourseAdmin)
admin.site.register(StudySession, StudySessionAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(ThreadModel, ThreadAdmin)
admin.site.register(MessageModel, MessageAdmin)
