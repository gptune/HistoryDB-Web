from django.urls import path
from django.urls import include

from . import views

app_name = "repo"
urlpatterns = [
    path('base/', views.base, name='base'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('userdashboard/', views.UserDashboard.as_view(), name='userdashboard'),
    path('entrydel/', views.EntryDel.as_view(), name='entrydel'),
    path('examples/', views.Examples.as_view(), name='examples'),
    path('upload/', views.Upload.as_view(), name='upload'),
    path('addapp/', views.AddApp.as_view(), name='addapp'),
    path('return/', views.base, name='return'),
    path('export/', views.Export.as_view(), name='export'),
    path('archive/<str:perf_data_uid>/', views.query, name='query'),
]
