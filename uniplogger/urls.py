from django.contrib import admin
from django.conf import settings
from django.urls import path, include,re_path

from rest_framework import routers,permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token

urlpatterns = [
    path('uniplogger-admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('accounts/', include('accounts.urls')),
    path('quests/', include('quests.urls')),
    path('planets/', include('planets.urls')),
    path('trashcans/', include('trashcans.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 문서화 = swagger/로 접속
schema_view = get_schema_view(
    openapi.Info(
        title="Uniplogger API",
        default_version='v1',
        description="Yapp IOS2 team ʕ•ᴥ•ʔ ",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
    ]