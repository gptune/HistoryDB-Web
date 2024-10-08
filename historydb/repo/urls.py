from django.urls import path
from django.urls import include

from . import views

app_name = "repo"
urlpatterns = [
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('user-dashboard/', views.UserDashboard.as_view(), name='user-dashboard'),
    path('surrogate-model/', views.SurrogateModel.as_view(), name='surrogate-model'),
    path('model-prediction/', views.ModelPrediction.as_view(), name='model-prediction'),
    path('analysis-dashing-parameter/', views.AnalysisDashingParameter.as_view(), name='analysis-dashing-parameter'),
    path('analysis-dashing-counter/', views.AnalysisDashingCounter.as_view(), name='analysis-dashing-counter'),
    path('sadashboard/', views.SADashboard.as_view(), name='sadashboard'),
    path('sobol-analysis/', views.SobolAnalysis.as_view(), name='sobol-analysis'),
    path('entryaccess/', views.EntryAccess.as_view(), name='entryaccess'),
    path('entrydel/', views.EntryDel.as_view(), name='entrydel'),
    path('upload/', views.Upload.as_view(), name='upload'),
    path('tuning-problems/', views.TuningProblems.as_view(), name='tuning-problems'),
    path('add-tuning-problem-select/', views.AddTuningProblemSelect.as_view(), name='add-tuning-problem-select'),
    path('add-tuning-problem/', views.AddTuningProblem.as_view(), name='add-tuning-problem'),
    path('add-tuning-problem-flexible/', views.AddTuningProblemFlexible.as_view(), name='add-tuning-problem-flexible'),
    path('add-reproducible-workflow/', views.AddReproducibleWorkflow.as_view(), name='add-reproducible-workflow'),
    path('add-tuning-category/', views.AddTuningCategory.as_view(), name='add-tuning-category'),
    path('applications/', views.Applications.as_view(), name='applications'),
    path('add-applications/', views.AddApplications.as_view(), name='add-applications'),
    path('architectures/', views.Architectures.as_view(), name='architectures'),
    path('add-architectures/', views.Architectures.as_view(), name='add-architectures'),
    path('machines/', views.Machines.as_view(), name='machines'),
    path('add-machine/', views.AddMachine.as_view(), name='add-machine'),
    path('analytical-models/', views.AnalyticalModels.as_view(), name='analytical-models'),
    path('add-analytical-model/', views.AddAnalyticalModel.as_view(), name='add-analytical-model'),
    path('export/', views.Export.as_view(), name='export'),
    path('export-all/', views.ExportAll.as_view(), name='export-all'),
    path('direct-download/', views.direct_download, name='direct-download'),
    path('direct-upload/', views.direct_upload, name='direct-upload'),
    path('api-test/', views.api_test, name='api-test'),
    path('archive/<str:perf_data_uid>/', views.query, name='query'),
]
