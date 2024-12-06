
from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.login_view, name='inspector_login'),
    path('view-reports/', views.view_reports, name='view_reports'),
    path('view-certificates/', views.view_certificates, name='view_certificates'),
    path('certificate/<int:certificate_id>/', views.certificate_detail, name='certificate_detail'),
    
    path('discussion-forum/', views.discussion_forum, name='discussion_forum'),
    path('discussion/<int:post_id>/', views.view_discussion, name='view_discussion'),
    path('create-post/', views.create_post, name='create_post'),
    path('create-reply/<int:post_id>/', views.create_reply, name='create_reply'),
]