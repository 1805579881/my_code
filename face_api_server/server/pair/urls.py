from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pose', views.pose, name='pose'),
    url(r'^xcmp', views.xcmp, name='xcmp'),
]
