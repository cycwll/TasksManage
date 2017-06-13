"""tasksM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from tasks import urls as task_urls
from tasks import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tasks/', include(task_urls)),
    url(r'^$', views.index, name='index'),
    url(r'^changepass/', views.change_pass, name='change_pass'),
    url(r'^check_code/', views.check_code, name='change_code'),
]
urlpatterns += (
   url(r'^resetpassword/$',
       auth_views.password_reset,
       name='password_reset'),
   url(r'^resetpassword/passwordsent/$',
       auth_views.password_reset_done,
       name='password_reset_done'),
   url(r'^reset/done/$',
       auth_views.password_reset_complete,
       name='password_reset_complete'),
   url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
       auth_views.password_reset_confirm,
       name='password_reset_confirm'),
   )