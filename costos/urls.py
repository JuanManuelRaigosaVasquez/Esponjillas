from django.urls import path
from . import views

app_name = 'costos'

urlpatterns = [
    path('', views.reporte_view, name='reporte'),
    path('api/calcular/', views.api_calcular, name='api_calcular'),
]
