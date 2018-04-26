# coding=utf-8
from django.conf.urls import url
from . import views

urlpatterns=[
    url('^add$',views.add),
    url('^$',views.index),
]