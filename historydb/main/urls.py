from django.urls import path
from django.urls import include

from . import views

from django.conf.urls import url
from django.contrib import admin

app_name = "main"
urlpatterns = [
    path('', views.index, name='index'),
    path('base', views.base, name='base'),
]
