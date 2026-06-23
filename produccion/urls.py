from django.urls import path
from . import views

app_name = 'produccion'

urlpatterns = [
    path('produccion/operator/', views.operator_view, name='operator'),
    path('produccion/dashboard/', views.dashboard_view, name='dashboard'),
    path('produccion/api/registrar/', views.api_registrar, name='api_registrar'),
    path('produccion/imprimir-sticker/<int:pk>/', views.imprimir_sticker, name='imprimir_sticker'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
