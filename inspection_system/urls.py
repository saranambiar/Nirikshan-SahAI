"""
URL configuration for inspection_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

# inspection_system/urls.py
from django.urls import path
from core import views
import inspector.views
import institute.views
from aicte_admin.views import login_view, aicte_logout

urlpatterns = [
    #common
    path('', views.homepage, name='homepage'),
    path('options/', views.options, name='options'),
    path('certificates/upload/', views.upload_certificate, name='upload_certificate'),
    
    path('inspector/', include('inspector.urls')),
    
    path('institute/', include('institute.urls')),


    #aicte
    path('aicte_login/', views.aicte_login, name='aicte_login'),
    path('aicte_login_check/', login_view, name='aicte_login_check'),
    path('aicte_logout/', aicte_logout ,name='aicte_logout'),
    path('aictemain/', views.aictemain, name='aictemain'),
    path('aicte_institutes/', views.aicte_institutes, name='aicte_institutes'),
    path('aicte_inspector/', views.aicte_inspector, name='aicte_inspector'),
    path('aicte_annexure/', views.aicte_annexure, name='aicte_annexure'),
    path('regionmap/', views.regionmap, name='regionmap'),
    path('region2/', views.region2, name='region2'),
    path('',include('aicte_admin.urls')),

    #inspector
    path('inspector_login/', views.inspector_login, name='inspector_login'),
    path('inspector_login_check',inspector.views.login_view,name='inspector_check'),
    path('inspector_logout/', inspector.views.inspector_logout ,name='inspector_logout'),
    path('view_image/', views.view_image, name='view_image'),
    path('annexure/', views.annexure, name="annexure"),
    path('report2/', views.report2, name="report2"),
    path('view_reports/', views.view_reports, name='view_reports'),
    path('discussion-forum/', views.discussion_forum, name='discussion_forum'),
    path('feedback/', views.feedback, name="feedback"),
    path('pattern_pred/',views.pattern_pred, name='pattern_pred'),
    path('view_classroom/',views.view_classroom, name='view_classroom'),
    path('view_lab/',views.view_lab, name='view_lab'),
    path('view_washroom/',views.view_washroom, name='view_washroom'),
    path('view_parking/',views.view_parking, name='view_parking'),
    path('view_pwd/',views.view_pwd, name='view_pwd'),
    path('view_canteen/',views.view_canteen, name='view_canteen'),
    path('view_mandatory/',inspector.views.view_mandatory, name='view_mandatory'),
    path('view_compliance/', inspector.views.view_compliance, name='view_compliance'),
    
    path('anamoly/', views.anamoly, name='anamoly'),
   


    
    #college
    path('college_login/', views.college_login, name='college_login'),
    path('college_login_check/',institute.views.login_view,name='college_login_check'),
    path('signup/', views.signup, name='signup'),
    path('college_signup_check/',institute.views.signup_view,name='college_signup_check'),
    path('index/', views.index, name='index'),
    path('upload_certificate/', views.upload_certificate, name='upload_certificate'),
    path('upload_certificate_check/',institute.views.upload_certificate,name='upload_certificates_check'),
    path('college_logout/', institute.views.college_logout ,name='college_logout'),
    path('upload_certificate/', views.upload_certificate, name='upload_certificate'),
    path('annexure/', views.annexure, name='annexure'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('feedback_view/', views.view_feedback, name='feedback_view'),
    path('classroom_upload/', views.classroom_upload, name='classroom_upload'),
    path('canteen_upload/', views.canteen_upload, name='canteen_upload'),
    path('pwd_upload/', views.pwd_upload, name="pwd_upload"),
    path('parking_upload/', views.parking_upload, name="parking_upload"),
    path('lab_upload/', views.lab_upload, name="lab_upload"),
    path('washroom_upload/', views.washroom_upload, name="washroom_upload"),
    path('report3/', views.report3, name="report3"),
    path('upload_excel/',views.upload_excel, name='upload_excel'),
    path('upload_mandatory_disclosure/',institute.views.upload_mandatory_dis, name='upload_mandatory_check'),



    # comment for uploading image route to cloudinary
    path('classroom_upload/upload_ui/', institute.views.u_i, name='upload_ui'),
]

