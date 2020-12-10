from django.urls import path
from django.urls import include

from . import views

app_name = "repo"
urlpatterns = [
    path('base/', views.base, name='base'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('examples/', views.examples, name='examples'),
    path('carousel/', views.carousel, name='carousel'),
    path('archive/<str:perf_data_uid>/', views.query, name='query'),
]
