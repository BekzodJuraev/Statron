"""
URL configuration for Statron project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include,re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.i18n import i18n_patterns
admin.site.site_header="Statron"
admin.site.site_title="Statron"
admin.site.index_title="Statron Adminstration Dashboard"
schema_view = get_schema_view(
    openapi.Info(
        title="Statron",
        default_version='v1',
        description="Your API description",

    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('__debug__/', include(debug_toolbar.urls))

]

urlpatterns += i18n_patterns( # Include your app's URLs
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('backend.urls')),
    prefix_default_language=False

)

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)