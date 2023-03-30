from django.urls import path
from django.urls import include

from . import views

app_name = "account"
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('profile/', views.ProfileDashboard.as_view(), name='profile'),
    path('access-tokens/', views.AccessTokens.as_view(), name='access-tokens'),
    path('add-access-token/', views.AddAccessToken.as_view(), name='add-access-token'),
    path('user-groups/', views.UserGroups.as_view(), name='user-groups'),
    path('add-group/', views.AddGroup.as_view(), name='add-group'),
    path('update-roles/', views.UpdateRoles.as_view(), name='update-roles'),
    path('invite-member/', views.InviteMember.as_view(), name='invite-member'),
    path('data/', views.DataDashboard.as_view(), name='data'),
    path('<str:username>/activate/', views.activate, name='activate'),
]
