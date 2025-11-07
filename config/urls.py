from django.contrib import admin
from django.urls import path
from data_analysis import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/dataset/overview/', views.dataset_overview),
    path('api/analysis/nulls/', views.null_values_analysis),
    path('api/analysis/duplicates/', views.duplicate_analysis),
    path('api/analysis/datatypes/', views.data_types_analysis),
    path('api/analysis/quality-score/', views.data_quality_score),
    path('api/analysis/statistics/', views.statistical_summary),
]