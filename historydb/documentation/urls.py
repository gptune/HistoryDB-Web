from django.urls import path
from django.urls import include

from . import views

app_name = "documentation"
urlpatterns = [
    path('documentation/<str:document_name>/', views.query, name='query'),
    path('', views.index, name='index'),
]
