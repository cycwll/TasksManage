from django.contrib import admin
from django.db import models
from django import forms
from .models import *

class NewUserAdmin(admin.ModelAdmin):
    search_fields = ['first_name','username']
    list_display = ('first_name','username', 'phone_number', 'email')

class ProjectAdmin(admin.ModelAdmin):
    list_filter = ['create_time']
    search_fields = ['name']
    list_display = ('name', 'leader_id', 'create_time')

class HistoryAdmin(admin.ModelAdmin):
    list_display = ('operation_user_id', 'operation_time', 'operation_description')

class TaskAdmin(admin.ModelAdmin):
    list_filter = ['create_time', 'project_id__name']
    search_fields = ['name','create_user_id__first_name', 'project_id__name']
    list_display = ('name','create_time','start_time','pre_finish_time','finish_time','create_user_id','execute_user_id','project_id','type')
    class Media:
        js = (
            '/static/js/tinymce/tiny_mce.min.js',
        )

admin.site.register(Project, ProjectAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(Task, TaskAdmin )
admin.site.register(NewUser, NewUserAdmin)
admin.site.register(TaskType)