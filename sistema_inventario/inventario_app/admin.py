from django.contrib import admin
from .models import Producto, MovimientoInventario, Categoria

admin.site.register(Producto)
admin.site.register(MovimientoInventario)
admin.site.register(Categoria)


# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'cantidad_stock')
    search_fields = ('nombre', 'codigo')
    list_filter = ('categoria',)

class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo_movimiento', 'cantidad', 'usuario', 'fecha')
    search_fields = ('producto__nombre', 'producto__codigo', 'usuario__username')
    list_filter = ('tipo_movimiento', 'fecha')
    
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)