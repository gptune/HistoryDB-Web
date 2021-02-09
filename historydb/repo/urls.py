from django.urls import path
from django.urls import include

from . import views

app_name = "repo"
urlpatterns = [
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('user-dashboard/', views.UserDashboard.as_view(), name='user-dashboard'),
    path('entryaccess/', views.EntryAccess.as_view(), name='entryaccess'),
    path('entrydel/', views.EntryDel.as_view(), name='entrydel'),
    path('upload/', views.Upload.as_view(), name='upload'),
    path('tuning-problems/', views.TuningProblems.as_view(), name='tuning-problems'),
    path('add-tuningproblmes/', views.AddTuningProblems.as_view(), name='add-tuningproblems'),
    path('applications/', views.Applications.as_view(), name='applications'),
    path('add-applications/', views.AddApplications.as_view(), name='add-applications'),
    path('architectures/', views.Architectures.as_view(), name='architectures'),
    path('add-architectures/', views.Architectures.as_view(), name='add-architectures'),
    path('machines/', views.Machines.as_view(), name='machines'),
    path('add-machines/', views.AddMachines.as_view(), name='add-machines'),
    path('user-groups/', views.UserGroups.as_view(), name='user-groups'),
    path('add-group/', views.AddGroup.as_view(), name='add-group'),
    path('update-roles/', views.UpdateRoles.as_view(), name='update-roles'),
    path('invite-member/', views.InviteMember.as_view(), name='invite-member'),
    path('export/', views.Export.as_view(), name='export'),
    path('archive/<str:perf_data_uid>/', views.query, name='query'),
]
