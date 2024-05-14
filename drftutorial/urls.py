"""
URL configuration for drftutorial project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings

from rest_framework.routers import SimpleRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from drftutorial.snippets import views

router = SimpleRouter()
router.register(r'snippets', views.SnippetViewSet, basename='snippet')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='api_schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api_schema'), name='api_docs'),

    path('api/token/', views.EnhancedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.EnhancedTokenRefreshView.as_view(), name='token_refresh'),

    path('api/v1/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns.append(
        path('debug/silk/', include('silk.urls', namespace='silk')),
    )
