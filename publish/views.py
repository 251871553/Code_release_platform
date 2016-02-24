#coding:utf-8

#from django.shortcuts import render
# Create your views here.

from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from models import User
import hashlib
from django.core.urlresolvers import reverse
from django.views import generic
import commands
import paramiko
from django.utils import timezone
import  MySQLdb
import  time
import  os

##########################公共函数#################################################
#form
class UserForm(forms.Form): 
    username = forms.CharField(label='登陆账户',max_length=100)
    password = forms.CharField(label='登陆密码',widget=forms.PasswordInput())

def  mysql(command):
    try:
       conn=MySQLdb.connect(host='localhost',user='root',passwd='',db='sa',port=3306,charset='utf8')
       cur=conn.cursor()
       cur.execute(command)
       info=cur.fetchall()
       cur.close()
       conn.close()
       for  i  in  info:
              return  i
    except Exception,e:
       return e
 
def para(shell):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect('192.168.15.80', username='root', password='71Dai!com23')
  stdin, stdout, stderr = ssh.exec_command(shell)
  cmd= stdout.readlines()
  ssh.close()
  return cmd


def getIP(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip =  request.META['HTTP_X_FORWARDED_FOR']
        return ip
    else:
        ip = request.META['REMOTE_ADDR']
        return ip


#########################功能模块####################################################

          
#regist
def regist(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            #获得表单数据
            username = uf.cleaned_data['username']
            #password = uf.cleaned_data['password']   #密码不加密，数据库中明文
            password = hashlib.sha1(uf.cleaned_data['password']).hexdigest()  #密文
            #查询是否重名
            user = User.objects.filter(username__exact = username)
            if user:
            #   return HttpResponse('用户名已经存在')
               result=False
               message='用户名已经存在 ！'
               return render_to_response('regist.html',{'msg':message,'result':result})
            else:
            #添加到数据库
             #  User.objects.create(username= username,password=password,lv1_id=6,lv2_id=4,lv3_id=2)
               User.objects.create(username= username,password=password,lv1_id=6,lv2_id=4,lv3_id=2)
               result=True
               message='注册成功 ！'
               return render_to_response('regist.html',{'msg':message,'result':result})
     #          return HttpResponse('regist success!!')
    else:
        uf = UserForm()
    return render_to_response('regist.html',{'uf':uf}, context_instance=RequestContext(req))

#login
def login(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            #获取表单用户密码
            username = uf.cleaned_data['username']
         #   password = uf.cleaned_data['password']
            password = hashlib.sha1(uf.cleaned_data['password']).hexdigest()  #密文
            #获取的表单数据与数据库进行比较
            user = User.objects.filter(username__exact = username,password__exact = password)
            if user:
                #比较成功，跳转index
                response = HttpResponseRedirect('/publish/index/')
                #将username写入浏览器cookie,失效时间为3600
                response.set_cookie('username',username,3600)
                return response
            else:
                #比较失败，还在login
                return HttpResponseRedirect('/publish/login/')
    else:
        uf = UserForm()
    return render_to_response('login.html',{'uf':uf},context_instance=RequestContext(req))

#登陆成功
def index(req):
    username = req.COOKIES.get('username','')
    if not username.strip():
       response = HttpResponseRedirect('/publish/login/')
       return response
    else: 
       return render_to_response('index.html' ,{'username':username})
#退出
def logout(req):
    #清理cookie里保存username
    response = HttpResponseRedirect('/publish/login/')
    response.delete_cookie('username')
    return response


#################################01线上测试环境############################
def publish_test_online(request,sh):
    shell='/bin/sh /root/%s.sh' %sh[:-4]
    username = request.COOKIES.get('username','')
    project=int(sh[-2])
    subentry=int(sh[-1])
    command='select lv1_id,lv2_id,lv3_id  from publish_user  where username="%s"' % username
    #查询用户所有权限
    authlv1=mysql(command)[0]
    #获取一，二，三级权限，结果为str，转化为int
    authlv2=int(mysql(command)[1])
    authlv3=int(mysql(command)[2])
    when=time.ctime()
    #查询两次数据库，主要是为了写日志，获取id对应的权限名字
    search1='select lv2  from publish_authv2  where id=%d' % authlv2
    search2='select lv3  from publish_authv3  where id=%d' % authlv3
    codename1=mysql(search1)[0].encode("utf-8")
    codename2=mysql(search2)[0].encode("utf-8")
    if  authlv1 == 1  or  authlv1 == 100  :   
        #判断一级权限
        if authlv2 == project:
        #判断二级权限
           if  authlv3  ==  subentry:
        #判断三级权限
               result=para(shell)
              #记录日志
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了线上测试环境%s项目%s代码，-- 成功！\n' % (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
           else:
               result=False
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了线上测试环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
        else:
           result=False
           f=file('/usr/local/sa/logs/publish.log','a')
           content='%s -- %s -- 发布了线上测试环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
           f.write(content)
           f.close()
           return render_to_response('publish.html' ,{'result':result,'username':username})
    else:
        result=False
        f=file('/usr/local/sa/logs/publish.log','a')
        content='%s -- %s -- 发布了线上测试环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
        f.write(content)
        f.close()
        return render_to_response('publish.html' ,{'result':result,'username':username})


#################################02线上生产环境############################
#V1.3
def publish_product_online(request,sh):
    shell='/bin/sh /root/%s.sh' %sh
    username = request.COOKIES.get('username','')
    command='select groups  from publish_user  where username="%s"' % username
    groupnumber=mysql(command)
    when=time.ctime()
    if  groupnumber == 2  or  groupnumber == 100  :
        result=para(shell)
        f=file('/usr/local/sa/logs/publish.log','a')
        content='%s -- %s -- 发布了线上生产环境代码，成功！\n' % (when,username)
        f.write(content)
        f.close()
        return render_to_response('publish.html' ,{'result':result,'username':username})
    else:
        result=False
        f=file('/usr/local/sa/logs/publish.log','a')
        content='%s -- %s -- 发布了线上生产环境代码，失败！  --权限不足\n' %  (when,username)
        f.write(content)
        f.close()
        return render_to_response('publish.html' ,{'result':result,'username':username})


#################################03线上开发环境############################
def publish_dev_online(request,sh):
    shell='/bin/sh /root/%s.sh' %sh[:-4]
    username = request.COOKIES.get('username','')
    project=int(sh[-2])
    subentry=int(sh[-1])
    command='select lv1_id,lv2_id,lv3_id  from publish_user  where username="%s"' % username
    authlv1=mysql(command)[0]
    authlv2=int(mysql(command)[1])
    authlv3=int(mysql(command)[2])
    when=time.ctime()
    search1='select lv2  from publish_authv2  where id=%d' % authlv2
    search2='select lv3  from publish_authv3  where id=%d' % authlv3
    codename1=mysql(search1)[0].encode("utf-8")
    codename2=mysql(search2)[0].encode("utf-8")
    if  authlv1 == 3  or  authlv1 == 100  :
        if authlv2 == project:
           if  authlv3  ==  subentry:
               result=para(shell)
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了线上开发环境%s项目%s代码，-- 成功！\n' % (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
           else:
               result=False
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了线上开发环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
        else:
           result=False
           f=file('/usr/local/sa/logs/publish.log','a')
           content='%s -- %s -- 发布了线上开发环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
           f.write(content)
           f.close()
           return render_to_response('publish.html' ,{'result':result,'username':username})
    else:
        result=False
        f=file('/usr/local/sa/logs/publish.log','a')
        content='%s -- %s -- 发布了线上开发环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
        f.write(content)
        f.close()
        return render_to_response('publish.html' ,{'result':result,'username':username})



#################################04线上演示环境############################
def publish_demo_online(request,sh):
    shell='/bin/sh /root/%s.sh' %sh[:-4]
    username = request.COOKIES.get('username','')
    project=int(sh[-2])
    subentry=int(sh[-1])
    command='select lv1_id,lv2_id,lv3_id  from publish_user  where username="%s"' % username
    authlv1=mysql(command)[0]
    authlv2=int(mysql(command)[1])
    authlv3=int(mysql(command)[2])
    when=time.ctime()
    search1='select lv2  from publish_authv2  where id=%d' % authlv2
    search2='select lv3  from publish_authv3  where id=%d' % authlv3
    codename1=mysql(search1)[0].encode("utf-8")
    codename2=mysql(search2)[0].encode("utf-8")
    if  authlv1 == 4  or  authlv1 == 100  :
        if authlv2 == project:
           if  authlv3  ==  subentry:
               result=para(shell)
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了线上演示环境%s项目%s代码，-- 成功！\n' % (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
           else:
               result=False
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了线上演示环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
        else:
           result=False
           f=file('/usr/local/sa/logs/publish.log','a')
           content='%s -- %s -- 发布了线上演示环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
           f.write(content)
           f.close()
           return render_to_response('publish.html' ,{'result':result,'username':username})
    else:
        result=False
        f=file('/usr/local/sa/logs/publish.log','a')
        content='%s -- %s -- 发布了线上演示环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
        f.write(content)
        f.close()
        return render_to_response('publish.html' ,{'result':result,'username':username})


#################################05内部测试环境############################
def publish_test_offline(request,sh):
    shell='/bin/sh /root/%s.sh' %sh[:-4]
    username = request.COOKIES.get('username','')
    project=int(sh[-2])
    subentry=int(sh[-1])
    command='select lv1_id,lv2_id,lv3_id  from publish_user  where username="%s"' % username
    authlv1=mysql(command)[0]
    authlv2=int(mysql(command)[1])
    authlv3=int(mysql(command)[2])
    when=time.ctime()
    search1='select lv2  from publish_authv2  where id=%d' % authlv2
    search2='select lv3  from publish_authv3  where id=%d' % authlv3
    codename1=mysql(search1)[0].encode("utf-8")
    codename2=mysql(search2)[0].encode("utf-8")
    if  authlv1 == 5  or  authlv1 == 100  :
        if authlv2 == project:
           if  authlv3  ==  subentry:
               result=para(shell)
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了内部测试环境%s项目%s代码，-- 成功！\n' % (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
           else:
               result=False
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了内部测试环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
        else:
           result=False
           f=file('/usr/local/sa/logs/publish.log','a')
           content='%s -- %s -- 发布了内部测试环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
           f.write(content)
           f.close()
           return render_to_response('publish.html' ,{'result':result,'username':username})
    else:
        result=False
        f=file('/usr/local/sa/logs/publish.log','a')
        content='%s -- %s -- 发布了内部测试环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
        f.write(content)
        f.close()
        return render_to_response('publish.html' ,{'result':result,'username':username})


#################################06临时环境############################
def publish_temp(request,sh):
    shell='/bin/sh /root/%s.sh' %sh[:-4]
    username = request.COOKIES.get('username','')
    project=int(sh[-2])
    subentry=int(sh[-1])
    command='select lv1_id,lv2_id,lv3_id  from publish_user  where username="%s"' % username
    authlv1=mysql(command)[0]
    authlv2=int(mysql(command)[1])
    authlv3=int(mysql(command)[2])
    when=time.ctime()
    search1='select lv2  from publish_authv2  where id=%d' % authlv2
    search2='select lv3  from publish_authv3  where id=%d' % authlv3
    codename1=mysql(search1)[0].encode("utf-8")
    codename2=mysql(search2)[0].encode("utf-8")
    if  authlv1 == 6  or  authlv1 == 100  :
        if authlv2 == project:
           if  authlv3  ==  subentry:
               result=para(shell)
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了线上临时环境%s项目%s代码，-- 成功！\n' % (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
           else:
               result=False
               f=file('/usr/local/sa/logs/publish.log','a')
               content='%s -- %s -- 发布了线上临时环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
               f.write(content)
               f.close()
               return render_to_response('publish.html' ,{'result':result,'username':username})
        else:
           result=False
           f=file('/usr/local/sa/logs/publish.log','a')
           content='%s -- %s -- 发布了线上临时环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
           f.write(content)
           f.close()
           return render_to_response('publish.html' ,{'result':result,'username':username})
    else:
        result=False
        f=file('/usr/local/sa/logs/publish.log','a')
        content='%s -- %s -- 发布了线上临时环境%s项目%s代码，-- 失败！  --权限不足\n' %  (when,username,codename1,codename2)
        f.write(content)
        f.close()
        return render_to_response('publish.html' ,{'result':result,'username':username})



#############################################审计，发布记录###########################
def publish_audit(request,sh):
     username = request.COOKIES.get('username','')
     result=commands.getoutput('tail  -n  20 /usr/local/sa/logs/publish.log').split('\n')[::-1] #转换成list再反转
     return render_to_response('audit.html' ,{'result':result,'username':username})
      
