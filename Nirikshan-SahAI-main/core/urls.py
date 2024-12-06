from django.urls import path
from . import views
from django.conf import settings

from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('options/', views.options, name='options'),
    path('logout/', views.logout_view, name='logout'),
    path('inspector/', include('inspector.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)