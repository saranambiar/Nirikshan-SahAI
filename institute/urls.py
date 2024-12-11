from django.urls import path
from . import views # Import feedback-specific views

urlpatterns = [
    path('view-feedback/', views.view_feedback, name='view_feedback'),
]
