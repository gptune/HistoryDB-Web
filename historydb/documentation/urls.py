from django.urls import path
from django.urls import include

from . import views

app_name = "documentation"
urlpatterns = [
    path('documentation/<str:document_name>/', views.query, name='query'),
    path('gptune-user-guide/', views.gptune_user_guide, name='gptune-user-guide'),
    path('gptune-tutorial-ecp2021/', views.gptune_tutorial_ecp2021, name='gptune-tutorial-ecp2021'),
    path('historydb-user-guide/', views.historydb_user_guide, name='historydb-user-guide'),
]
