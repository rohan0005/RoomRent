from django.contrib import admin
from django.urls import path, include

#  Import modules for serving static files
from django.conf import settings
from django.conf.urls.static import static

# Custom 404 error view
handler404 = 'core.views.error_404' 
# Custom 500 error view
handler500 = 'core.views.error_500' 



urlpatterns = [
    path('superadmin/', admin.site.urls),
    #include the URL patterns from another apps 
    path('', include("users.urls")),  
    path('', include("core.urls")),
    path('', include("room.urls")),
    path('', include("payment.urls")),
]

# For viewing image through url
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
