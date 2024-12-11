from django.urls import path
from . import views # Import feedback-specific views
from .views import u_i

urlpatterns = [
    path('view-feedback/', views.view_feedback, name='view_feedback'),
    path('institute/download/manual-report/<str:feedback_id>/', views.download_manual_report, name='download_manual_report'),
    path('/upload/', u_i, name='upload_image'),
]
