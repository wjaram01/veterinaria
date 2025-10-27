# mi_sitio/urls.py

from django.contrib import admin
from django.urls import path, include  # Importa 'include'
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Opcional: Asegúrate de que los estáticos también se sirvan (si no están ya)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)