from django import forms
from .models import *

class LoginForm(forms.Form):
	uid = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' ,'id':'uid', 'placeholder': 'Username'}))
	pwd = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control' ,'id':'pwd', 'placeholder': 'Password'}))

class RegisterForm(forms.Form):
	username = forms.CharField(label='username', max_length=100,
		widget=forms.TextInput(attrs={'id':'username', 'onblur': 'authentication()'}))
	email = forms.EmailField()
	password1 = forms.CharField(widget=forms.PasswordInput)
	password2 = forms.CharField(widget=forms.PasswordInput)

class ChangeForm(forms.Form):
    old_password = forms.CharField(label='原密码',widget=forms.PasswordInput())
    new_password = forms.CharField(label='新密码',widget=forms.PasswordInput())

class SetInfoForm(forms.Form):
	username = forms.CharField()

class CommmentForm(forms.Form):
	comment = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': '120', 'rows': '12'}))

class SearchForm(forms.Form):
	keyword = forms.CharField(widget=forms.TextInput)

class MessageForm(forms.Form):
	message = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",}))

class CreateTaskForm(forms.Form):
    task_name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control","placeholder":"请输入任务名称",}))
    project_name = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control',}),queryset=Project.objects.all(),empty_label='请选择项目名称...')
    #initial=3,设置默认值，empty_label 设置提示，如果是select 默认是-----
    tasktype = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control',}),initial=2,
                                      queryset=TaskType.objects.all(),empty_label='请选择任务类型...')
    task_user = forms.ModelMultipleChoiceField(NewUser.objects.all(),label='相关人', required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control',}),required=True)


