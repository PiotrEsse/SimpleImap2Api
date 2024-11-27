from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include('api.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api-auth/', include('rest_framework.urls')),
    
    # Web interface URLs
    path('', include('emails.urls')),
    
    # Redirect root to email list
    path('', RedirectView.as_view(pattern_name='email_list', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add debug toolbar URLs if in debug mode
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
