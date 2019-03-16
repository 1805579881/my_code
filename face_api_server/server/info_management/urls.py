#!/usr/bin/python
#!-*-coding:UTF8-*-
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.PeopleIndex.as_view(), name="info_management_index"),
    url(r'^create$', views.PeopleCreate.as_view(), name="info_management_create"),
    url(r'^delete/', views.delete_info,name="info_management_delete"),
    url(r'^detail/', views.detail_info, name="info_management_detail"),
    url(r'^edit/', views.edit_info,name="info_management_edit"),
    url(r'^demo/', views.PeopleDemo.as_view(), name="info_management_demo"),
]








