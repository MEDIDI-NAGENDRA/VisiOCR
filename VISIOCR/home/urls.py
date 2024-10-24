from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('generate-pass/', views.generate_pass, name='generate_pass'),  # Generate visitor pass
    path('validate-pass/', views.validate_pass, name='validate_pass'),  # Validate visitor pass
    path('view-and-download-pass/', views.view_and_download_pass, name='view_and_download_pass'),  # View and download visitor pass
    path('download-pass/<str:pass_id>/', views.download_pass, name='download_pass'), 
     path('validate-pass/', views.validate_pass, name='validate_pass'), # Download specific visitor pass PDF
]
