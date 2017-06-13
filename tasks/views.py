from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from urllib.parse import urljoin
import datetime
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import *
import os
from django.http import StreamingHttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives

def index(request):
    project_id = request.GET.get("project_id")
    if  project_id is None:
        latest_article_list1 = Task.objects.query_by_stat()
    else:
        latest_article_list1 = Task.objects.filter(project_id = project_id).order_by('stat','-create_time')
    projects = Project.objects.all()
    paginator = Paginator(latest_article_list1, 15)
    page = request.GET.get('page')
    try:
        latest_article_list = paginator.page(page)
    except PageNotAnInteger:
        latest_article_list = paginator.page(1)
    except  EmptyPage:
        latest_article_list = paginator.page(paginator.num_pages)
    loginform = LoginForm()
    messageform = MessageForm()
    context = {'latest_article_list': latest_article_list,'projects':projects, 'messageform':messageform,'loginform': loginform}
    return render(request, 'index.html', context)

def task(request,task_id):
    '''
    try:   # since visitor input a url with invalid id
        article = Article.objects.get(pk=task_id)  # pk???
    except Article.DoesNotExist:
        raise Http404("Article does not exist")
    '''  # shortcut:
    task = get_object_or_404(Task, id=task_id)
    content = task.description
    relate_users = task.users.all()
    commentform = CommmentForm()
    loginform = LoginForm()
    comments = History.objects.filter(task_id= task_id).order_by('-operation_time')
    attachments = Attachment.objects.filter(task_id = task_id)

    return render(request, 'article_page.html', {
        'article': task,
        'loginform': loginform,
        'commentform': commentform,
        'content': content,
        'comments': comments,
        'relate_users': relate_users,
        'attachments':attachments
    })

@login_required
def receive_task(request, task_id):
    logged_user= request.user
    task = get_object_or_404(Task, id=task_id)
    task.execute_user_id = logged_user

    if request.POST.get('Submit') == '保存操作':
        task.create_time = task.create_time
        task.stat = 1
    elif request.POST.get('Submit') == '开始任务':
        task.start_time = timezone.now()
        task.stat = 1
    elif request.POST.get('Submit') == '完成':
        task.finish_time = timezone.now()
        task.stat = 2
    task.save()

    form = CommmentForm(request.POST)
    if form.is_valid():
        new_comment = form.cleaned_data['comment']
        history = History()
        history.operation_time = timezone.now()
        history.operation_description = new_comment
        history.operation_user_id = request.user
        history.task_id = task
        history.save()
    else:
        new_comment = str(request.POST.get('Submit'))
        history = History()
        history.operation_time = timezone.now()
        history.operation_description = new_comment
        history.operation_user_id = request.user
        history.task_id = task
        history.save()
    #处理上传的附件
    myFiles = request.FILES.getlist("myfile", None)
    for myFile in myFiles:
        if myFile:
            task_id = str(task.id)
            if os.path.isdir(os.path.join("download", task_id)):
                pass
            else:
                os.mkdir(os.path.join("download", task_id))
            destination = open(os.path.join("download", task_id, myFile.name),
                               'wb+')
            for chunk in myFile.chunks():
                destination.write(chunk)
            destination.close()
            attachment = Attachment()
            attachment.attachment = os.path.join(task_id, myFile.name)
            attachment.task = task
            attachment.filename = myFile.name
            attachment.save()

    #给任务相关人发送邮件
    user = NewUser.objects.get(id=task.create_user_id_id)
    user_email = user.email
    relate_user_list = [user_email,'cycwll@163.com','75678489@qq.com']
    relate_users = task.users.all()
    for relate_user in relate_users:
        relate_user_list.append(relate_user.email)

    subject = '任务状态更新：' + str(task.name)
    text_content = ''
    html_content = '状态：' + str(task.get_stat_display()) + history.operation_description + "<hr>" + task.description
    from_email = '任务管理系统<cycwll@163.com>'
    recipient_list = relate_user_list
    send_html_mail(subject, text_content, html_content, from_email, recipient_list)

    return redirect('/tasks/')

@login_required
def comment(request, task_id):
	form  = CommmentForm(request.POST)
	url = urljoin('/task/', task_id)
	if form.is_valid():
		user = request.user
		article = Task.objects.get(id=task_id)
		new_comment = form.cleaned_data['comment']
		c = comment(content=new_comment, article_id=task_id)
		c.user = user
		c.save()
		article.comment_num += 1
	return redirect(url)

@login_required
def CreateTask(request):
    if request.method == 'POST':
        ctaskform = CreateTaskForm(request.POST)
        if ctaskform.is_valid():
            task_name = ctaskform.cleaned_data['task_name']
            project_name = ctaskform.cleaned_data['project_name']
            tasktype = ctaskform.cleaned_data['tasktype']
            description = ctaskform.cleaned_data['description']
            task_users = ctaskform.cleaned_data['task_user']
            create_user = request.user
            task=Task()
            task.name = task_name
            task.project_name = project_name
            task.create_time = datetime.datetime.now()
            task.project_id = project_name
            task.type = tasktype
            task.create_user_id = create_user
            task.description = description
            task.save()
            for user in task_users:
                task.users.add(user)
            task.save()
            myFiles = request.FILES.getlist("myfile", None)
            for myFile in myFiles:
                if myFile:
                    task_id = str(task.id)
                    if os.path.isdir(os.path.join("download", task_id)):
                        pass
                    else:
                        os.mkdir(os.path.join("download", task_id))
                    destination = open(os.path.join("download", task_id, myFile.name),'wb+')
                    for chunk in myFile.chunks():
                        destination.write(chunk)
                    destination.close()
                    attachment = Attachment()
                    attachment.attachment = os.path.join( task_id , myFile.name)
                    attachment.task = task
                    attachment.filename = myFile.name
                    attachment.save()
            relate_user_list = [request.user.email,'cycwll@163.com','75678489@qq.com']
            relate_users = task.users.all()
            for relate_user in relate_users:
                relate_user_list.append(relate_user.email)
            subject = '新任务：' + str(task.name)
            text_content = ''
            html_content = '状态:'+ str(task.get_stat_display())  + task.description
            from_email = '任务管理系统<cycwll@163.com>'
            recipient_list = relate_user_list
            send_html_mail(subject,text_content,html_content,from_email,recipient_list)
            return redirect('/tasks/')
    else:
        ctaskform = CreateTaskForm()
        return render(request, 'createtask.html', {'ctaskform':ctaskform})

@login_required
def download(request):
    filename = request.get_full_path().split('/')[4]
    task_id  = request.get_full_path().split('/')[3]
    file_name = str("download\\" + task_id + '\\' +filename)
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,"rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    response = StreamingHttpResponse(file_iterator(file_name))
    return response


#发送html邮件
def send_html_mail(subject, text_content,html_content,from_email, recipient_list):
    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

#图片验证码
def check_code(request):
    import io
    from tasks import check_code as CheckCode
    stream = io.BytesIO()
    img, code = CheckCode.create_validate_code()
    img.save(stream, "png")
    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())

def message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            MSG = MessageBoard()
            MSG.message = message
            MSG.save()
            url = request.META['HTTP_REFERER']
    return redirect(url)

#登录模块
def log_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['uid']
            password = form.cleaned_data['pwd']
            user = authenticate(username=username, password=password)
            input_code = request.POST.get('check_code')
            if input_code.upper() != request.session['CheckCode'].upper():
                return render(request, 'login.html', {'form': form, 'error': "验证码错误!"})
            if user is not None:
                login(request, user)
                url = request.POST.get('source_url', '/tasks')
                return redirect(url)
            else:
                return render(request, 'login.html', {'form': form, 'error': "用户名或密码错误!"})
        else:
            return render(request, 'login.html', {'form': form, 'error': "用户名或密码错误!"})

@login_required
def log_out(request):
    url = request.POST.get('source_url', '/tasks/')
    logout(request)
    return redirect(url)


def register(request):
    error1 = "this name is already exist"
    valid = "this name is valid"

    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if request.POST.get('raw_username', 'erjgiqfv240hqp5668ej23foi') != 'erjgiqfv240hqp5668ej23foi':  # if ajax
            try:
                user = NewUser.objects.get(username=request.POST.get('raw_username', ''))
            except ObjectDoesNotExist:
                return render(request, 'register.html', {'form': form, 'msg': valid})
            else:
                return render(request, 'register.html', {'form': form, 'msg': error1})
        else:
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password1 = form.cleaned_data['password1']
                password2 = form.cleaned_data['password2']
                if password1 != password2:
                    return render(request, 'register.html', {'form': form, 'msg': "two password is not equal"})
                else:
                    user = NewUser(username=username, email=email, password=make_password(password1,None,'pbkdf2_sha256'))
                    user.save()
                    # return render(request, 'login.html', {'success': "you have successfully registered!"})
                    return redirect('/tasks/login')
            else:
                return render(request, 'register.html', {'form': form})

@login_required
def change_pass(request):
    logined_user = request.user
    if request.method == 'POST':
        uf = ChangeForm(request.POST)
        if uf.is_valid():
            old_password = uf.cleaned_data['old_password']
            new_password = uf.cleaned_data['new_password']

            ##判断用户原密码是否匹配
            if logined_user and check_password(old_password,logined_user.password):
                logined_user.password = make_password(new_password,None,'pbkdf2_sha256')
                logined_user.save()
                info = '密码修改成功!'
            else:
                info = '请检查原密码是否输入正确!'

        return HttpResponse(info)
    else:
        uf = ChangeForm()
    return render(request,'change.html', {'uf': uf,'username':logined_user})