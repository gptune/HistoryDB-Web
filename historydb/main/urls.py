from django.urls import path
from django.urls import include

from . import views

from django.conf.urls import url
from django.contrib import admin

app_name = "main"
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('about', views.about, name='about'),
    path('publications', views.publications, name='publications'),
    path('acknowledgement', views.acknowledgement, name='acknowledgement'),
    path('membership', views.membership, name='membership'),
    path('gptune-tutorial-ecp2021', views.gptune_tutorial_ecp2021, name='gptune-tutorial-ecp2021'),
    path('release', views.release, name='release'),
    path('base', views.base, name='base'),
]
