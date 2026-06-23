from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.stock_view, name='stock'),
    path('materia-prima/', views.materia_prima_view, name='materia_prima'),
    path('api/stock-actual/', views.api_stock_actual, name='api_stock_actual'),
]
