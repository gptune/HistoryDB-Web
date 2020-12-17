from django.urls import path
from django.urls import include

from . import views

app_name = "repo"
urlpatterns = [
    path('base/', views.base, name='base'),
    path('display/', views.display, name='display'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('examples/', views.examples, name='examples'),
    path('export/', views.Export.as_view(), name='export'),
    path('carousel/', views.carousel, name='carousel'),
    path('archive/<str:perf_data_uid>/', views.query, name='query'),
]
