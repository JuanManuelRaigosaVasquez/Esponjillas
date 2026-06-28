from django.urls import path
from . import views

app_name = 'produccion'

urlpatterns = [
    path('produccion/operator/', views.operator_view, name='operator'),
    path('produccion/registro-rapido/', views.registro_rapido_view, name='registro_rapido'),
    path('produccion/dashboard/', views.dashboard_view, name='dashboard'),
    path('produccion/analiticas/', views.analiticas_view, name='analiticas'),
    path('produccion/api/analiticas/', views.api_analiticas, name='api_analiticas'),
    path('produccion/api/registrar/', views.api_registrar, name='api_registrar'),
    path('produccion/api/registrar-rapido/', views.api_registrar_rapido, name='api_registrar_rapido'),
    path('produccion/imprimir-sticker/<int:pk>/', views.imprimir_sticker, name='imprimir_sticker'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
