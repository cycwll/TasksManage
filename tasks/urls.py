from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.log_in, name='login'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^(?P<task_id>[0-9]+)/$', views.task, name='task'),
    url(r'^(?P<task_id>[0-9]+)/receive_task/$', views.receive_task, name='receive_task'),
    url(r'^createtask/',views.CreateTask,name='create_task'),
    url(r'^message/',views.message,name='message'),
    url(r'^download/',views.download,name='download'),
    url(r'^tinymce/', include('tinymce.urls')),
    ]
urlpatterns += staticfiles_urlpatterns()
