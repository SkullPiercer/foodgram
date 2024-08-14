from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    re_path(
        r'^s/',
        include('django_short_url.urls', namespace='django_short_url')
    ),
]
