"""pengfeng URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
import rest_framework.permissions as permissions
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authtoken import views
from rest_framework_bulk.routes import BulkRouter

from rest.views import CustomPersonViewSet, PersonViewSet, RecordViewSet, DepartmentViewSet
from sync.views import DeviceViewSet

standard_router = BulkRouter()
standard_router.register(r'people', PersonViewSet, base_name='person')
standard_router.register(r'records', RecordViewSet, base_name='record')
standard_router.register(r'custom_people', CustomPersonViewSet, base_name='custom_person')
standard_router.register(r'devices', DeviceViewSet, base_name='device')
standard_router.register(r'department', DepartmentViewSet, base_name='department')


schema_view = get_schema_view(
    openapi.Info(
        title="Face API",
        default_version='v1',
        description="PerfXLab REST API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
rest_patterns = [
    path('', include(standard_router.urls)),
    re_path(r'^api-token-auth/$', views.obtain_auth_token),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None),
            name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc')
]
urlpatterns = [
                  path('', include('enhanced_ui.urls')),
                  path('admin/', admin.site.urls),
                  path('api/v1/', include(rest_patterns)),
                  path('rest/', include('rest.urls')),
                  path('sync/', include('sync.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

