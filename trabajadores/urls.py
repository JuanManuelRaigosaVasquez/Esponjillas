from django.urls import path
from . import views

app_name = 'trabajadores'

urlpatterns = [
    path('', views.lista_view, name='lista'),
    path('crear/', views.crear_view, name='crear'),
    path('<int:pk>/editar/', views.editar_view, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_view, name='eliminar'),
]
