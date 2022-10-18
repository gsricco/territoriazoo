
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path("api_schema/", get_schema_view(title="API SCHEMA", description="Guide to Territory_Zoo API"),
         name="api_schema"),
    path('docs/', TemplateView.as_view(template_name='docs.html',
                                       extra_context={'schema_url': 'api_schema'}), name='swagger-ui'),
    path('admin-panel/', admin.site.urls),
    re_path(r'^chaining/', include('smart_selects.urls')),
    path('api/', include('main.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
