from django.urls import path
from . import views

app_name = 'tercerizacion'

urlpatterns = [
    path('', views.lista_view, name='lista'),
    path('crear/', views.crear_view, name='crear'),
    path('<int:pk>/', views.detalle_view, name='detalle'),
    path('<int:pk>/cerrar/', views.cerrar_view, name='cerrar'),
]
