from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda r: redirect('produccion:operator')),
    path('', include('produccion.urls')),
    path('inventario/', include('inventario.urls')),
    path('tercerizacion/', include('tercerizacion.urls')),
    path('costos/', include('costos.urls')),
]
