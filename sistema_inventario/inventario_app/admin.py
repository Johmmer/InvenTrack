from django.contrib import admin
from .models import Producto, MovimientoInventario, Categoria

admin.site.register(Producto)
admin.site.register(MovimientoInventario)
admin.site.register(Categoria)

@admin.register(Producto)


# Register your models here.
