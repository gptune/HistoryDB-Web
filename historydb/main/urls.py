from django.urls import path
from django.urls import include

from . import views

from django.conf.urls import url
from django.contrib import admin

app_name = "main"
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('about', views.about, name='about'),
    path('publications', views.publications, name='publications'),
    url(r'^docs/', include('docs.urls')),
    path('acknowledgement', views.acknowledgement, name='acknowledgement'),
    path('membership', views.membership, name='membership'),
    path('gptune-tutorial-ecp2021', views.gptune_tutorial_ecp2021, name='gptune-tutorial-ecp2021'),
    path('gptune-tutorial-ecp2022', views.gptune_tutorial_ecp2022, name='gptune-tutorial-ecp2022'),
    path('gptune-tutorial-ecp2023', views.gptune_tutorial_ecp2023, name='gptune-tutorial-ecp2023'),
    path('release', views.release, name='release'),
    path('terms-of-use', views.terms_of_use, name='terms-of-use'),
    path('license', views.license, name='license'),
    path('examples', views.Examples.as_view(), name='examples'),
    path('base', views.base, name='base'),
]
