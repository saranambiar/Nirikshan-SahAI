from django.urls import path,re_path
from . import views

urlpatterns = [
    path('inspectors/', views.inspector_list, name='inspector_list'),
    path('inspectors/create/', views.inspector_create, name='inspector_create'),
    re_path(r'^inspectors/(?P<pk>[0-9a-fA-F]{24})/$', views.inspector_detail, name='inspector_detail'),
    re_path(r'^inspectors/(?P<pk>[0-9a-fA-F]{24})/update/$', views.inspector_update, name='inspector_update'),
    re_path(r'^inspectors/(?P<pk>[0-9a-fA-F]{24})/delete/$', views.inspector_delete, name='inspector_delete'),
    path('institutes/', views.institute_list, name='institute_list'),
    re_path(r'^institutes/(?P<pk>[0-9a-fA-F]{24})/$', views.institute_detail, name='institute_detail'),
    re_path(r'^institutes/(?P<pk>[0-9a-fA-F]{24})/update/$', views.institute_update, name='institute_update')

]