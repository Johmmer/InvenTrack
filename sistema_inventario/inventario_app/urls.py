from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('productos/', views.productos, name='productos'),
    path('productos/nuevo/', views.producto_nuevo, name='producto_nuevo'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='eliminar_producto'),
    path('movimientos/', views.movimientos, name='movimientos'),
    path('movimientos/nuevo/', views.movimiento_nuevo, name='registrar_movimiento'),
    path('movimientos/exportar/', views.movimientos_exportar, name='exportar_movimientos'),
]
