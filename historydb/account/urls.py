from django.urls import path
from django.urls import include

from . import views

app_name = "account"
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.ProfileDashboard.as_view(), name='profile'),
    path('group/', views.GroupDashboard.as_view(), name='group'),
    path('addgroup/', views.AddGroupDashboard.as_view(), name='addgroup'),
    path('updategroup/', views.UpdateGroupDashboard.as_view(), name='updategroup'),
    path('data/', views.DataDashboard.as_view(), name='data'),
    path('<str:username>/activate/', views.activate, name='activate'),
]
