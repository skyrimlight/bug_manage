"""
URL configuration for bug_manage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from web.view import user_info_view, home_view, project_view, manage_view, wiki_view, file_view, setting_view, \
    issues_view, dashboard_view, statistics_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path('register/', user_info_view.user_register, name='register'),
    path('send_sms/', user_info_view.send_sms, name='send_sms'),
    path('login/', user_info_view.user_login, name='login'),
    path('login/sms/', user_info_view.user_login_by_sms, name='login_sms'),
    path('image_code/', user_info_view.image_code, name='image_code'),
    path('logout/', user_info_view.logout, name='logout'),

    path('index/', home_view.index, name='index'),
    path('price/', home_view.price, name='price'),
    path('payment/<policy_id>/', home_view.payment, name='payment'),
    path('pay/', home_view.pay, name='pay'),
    path('pay/notify/', home_view.pay_notify, name='pay_notify'),
    path('pay/return/', home_view.pay_return, name='pay_return'),

    # 项目列表
    path('project_list/', project_view.project_list, name='project_list'),
    path('project_star/<project_type>/<project_id>', project_view.project_star, name='project_star'),
    path('project_unstar/<project_id>', project_view.project_unstar, name='project_unstar'),
    # path('project_add/', project_view.project_add, name='project_add'),
    # 项目管理
    # wiki管理
    path('manage/<project_id>/wiki/', wiki_view.wiki, name='wiki'),
    path('manage/<project_id>/wiki_add/', wiki_view.wiki_add, name='wiki_add'),
    path('manage/<project_id>/wiki_edit/<wiki_id>', wiki_view.wiki_edit, name='wiki_edit'),
    path('manage/<project_id>/wiki_delete/<wiki_id>', wiki_view.wiki_delete, name='wiki_delete'),
    path('manage/<project_id>/wiki_catalog/', wiki_view.wiki_catalog, name='wiki_catalog'),
    path('manage/<project_id>/wiki_upload/', wiki_view.wiki_upload, name='wiki_upload'),
    # 文件管理
    # path('manage/<project_id>/wiki_detail/<wiki_id>', wiki_view.wiki_detail, name='wiki_detail'),
    path('manage/<project_id>/file/', file_view.file, name='file'),
    path('manage/<project_id>/file_delete/', file_view.file_delete, name='file_delete'),
    path('manage/<project_id>/cos/credential', file_view.cos_credential, name='cos_credential'),
    path('manage/<project_id>/file/post', file_view.file_post, name='file_post'),
    path('manage/<project_id>/file/download/<file_id>', file_view.file_download, name='file_download'),
    # 设置管理
    path('manage/<project_id>/setting/', setting_view.setting, name='setting'),
    path('manage/<project_id>/setting/delete/', setting_view.setting_delete, name='setting_delete'),

    # 问题管理
    path('manage/<project_id>/issues/', issues_view.issues, name='issues'),
    path('manage/<project_id>/issues_detail/<issues_id>/', issues_view.issues_detail, name='issues_detail'),
    path('manage/<project_id>/issues_record/<issues_id>/', issues_view.issues_record, name='issues_record'),
    path('manage/<project_id>/issues_change/<issues_id>/', issues_view.issues_change, name='issues_change'),
    path('manage/<project_id>/invite/url/', issues_view.invite_url, name='invite_url'),
    path('invite/join/<code>/', issues_view.invite_join, name='invite_join'),

    path('manage/<project_id>/dashboard/', dashboard_view.dashboard, name='dashboard'),
    path('manage/<project_id>/issues/chart/', dashboard_view.issues_chart, name='issues_chart'),
    path('manage/<project_id>/statistics/', statistics_view.statistics, name='statistics'),
    path('manage/<project_id>/statistics_priority/', statistics_view.statistics_priority, name='statistics_priority'),
    path('manage/<project_id>/statistics_project_user/', statistics_view.statistics_project_user,
         name='statistics_project_user'),

]
