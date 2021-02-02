from django.urls import path
from django.urls import include

from . import views

app_name = "repo"
urlpatterns = [
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('userdashboard/', views.UserDashboard.as_view(), name='userdashboard'),
    path('entryaccess/', views.EntryAccess.as_view(), name='entryaccess'),
    path('entrydel/', views.EntryDel.as_view(), name='entrydel'),
    path('upload/', views.Upload.as_view(), name='upload'),
    path('addapp/', views.AddApp.as_view(), name='addapp'),
    path('export/', views.Export.as_view(), name='export'),
    path('archive/<str:perf_data_uid>/', views.query, name='query'),
]
