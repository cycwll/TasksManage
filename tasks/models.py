from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from tinymce import models as tinymce_models

class TaskManager(models.Manager):
    def query_by_column(self, column_id):
        query = self.get_queryset().filter(column_id=column_id)
        return query

    def query_by_user(self, user_id):
        user = User.objects.get(id=user_id)
        article_list = user.article_set.all()
        return article_list

    def query_by_polls(self):
        query = self.get_queryset().order_by('poll_num')
        return query

    def query_by_time(self):
        query = self.get_queryset().order_by('-create_time')
        return query

    def query_by_stat(self):
        query = self.get_queryset().order_by('stat','-create_time')
        return query

    def query_by_keyword(self, keyword):
        query = self.get_queryset().filter(name__contains=keyword)
        return query

#Users
class NewUser(AbstractUser):
    phone_number = models.CharField(default='',max_length=15)

    def __str__(self):
        return self.first_name

#Projects
class Project(models.Model):
    name = models.CharField(max_length=128, verbose_name= u'项目名称')
    leader_id = models.ForeignKey(NewUser, verbose_name= u'项目经理')
    create_time = models.DateTimeField(default=timezone.now, verbose_name= u'创建时间')
    users = models.ManyToManyField(NewUser,related_name='NewUser' )
    def __str__(self):
        return self.name

#Task's type
class TaskType(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=512)

    def __str__(self):
        return self.name
#Tasks
class Task(models.Model):
    name = models.CharField(max_length=128,verbose_name= u'任务名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name= u'创建时间')
    start_time = models.DateTimeField(null=True, verbose_name= u'开始时间')
    pre_finish_time = models.DateTimeField(null=True,verbose_name= u'预计完成时间')
    finish_time = models.DateTimeField(null=True,verbose_name= u'完成时间')
    create_user_id = models.ForeignKey(NewUser, verbose_name=u"创建人", related_name=u'创建人')
    execute_user_id = models.ForeignKey(NewUser, null=True, verbose_name=u"执行人", related_name=u'执行人')
    statut_choice = (
        (0, u'未开始'),
        (1, u'进行中'),
        (2, u'已完成')
    )
    stat = models.IntegerField(default=0, choices=statut_choice,verbose_name = u'任务状态')
    project_id = models.ForeignKey(Project,verbose_name = u'所属项目')
    type = models.ForeignKey(TaskType, default=2 ,blank=False,verbose_name = u'任务类型')
    description = tinymce_models.HTMLField(blank=True,null=True)
    users = models.ManyToManyField(NewUser,verbose_name='相关人')


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'task'
        verbose_name_plural = 'task'

    objects = TaskManager()


#Task's History
class History(models.Model):
    task_id = models.ForeignKey(Task)
    operation_user_id = models.ForeignKey(NewUser)
    operation_time = models.DateTimeField()
    operation_description = tinymce_models.HTMLField(default=' ')
    def __str__(self):
        return str(self.operation_time)
#attach
class Attachment(models.Model):
    filename = models.CharField(null=True,max_length=200,verbose_name = u'文件名')
    attachment = models.FileField(upload_to='%Y/%m/%d')
    task = models.ForeignKey(Task)
    def __str__(self):
        return str(self.attachment)

#bug
class MessageBoard(models.Model):
    message = models.TextField(max_length=512)