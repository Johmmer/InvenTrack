from django import forms
from .models import Producto, MovimientoInventario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'codigo', 'categoria', 'precio_compra', 'precio_venta', 'cantidad']

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo', 'cantidad', 'observacion']
