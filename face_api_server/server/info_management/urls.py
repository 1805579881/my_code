#!/usr/bin/python
#!-*-coding:UTF8-*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create/$', views.create_info, name='index'),
]