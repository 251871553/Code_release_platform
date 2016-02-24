#coding:utf-8


from django.conf.urls import url
from publish import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/$',views.login,name = 'login'),
    url(r'^regist/$',views.regist,name = 'regist'),
    url(r'^index/$',views.index,name = 'index'),
    url(r'^logout/$',views.logout,name = 'logout'),
    #线上测试
    url(r'^(?P<sh>totest[\s\S]+)/$', views.publish_test_online, name='publish_test_online'),   
    #线上生产
    url(r'^(?P<sh>toidc[\s\S]+)/$', views.publish_product_online, name='publish_product_online'),
    #线上开发
    url(r'^(?P<sh>todev_idc[\s\S]+)/$', views.publish_dev_online, name='publish_dev_online'),
    #线上演示
    url(r'^(?P<sh>todemo[\s\S]+)/$', views.publish_demo_online, name='publish_demo_online'),
    #内部测试
    url(r'^(?P<sh>todev_beta[\s\S]+)/$', views.publish_test_offline, name='publish_test_offline'),
    #临时
    url(r'^(?P<sh>totemp[\s\S]+)/$', views.publish_temp, name='publish_temp'),
#51p2b
    url(r'^(?P<sh>newto[\s\S]+)/$', views.publish_temp, name='publish_temp'),
    #审计
    url(r'^(?P<sh>audit)/$', views.publish_audit, name='publish_audit'),

]
