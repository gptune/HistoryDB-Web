from django.urls import path
from django.urls import include

from . import views

app_name = "account"
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('<str:username>/activate/', views.activate, name='activate'),
]
