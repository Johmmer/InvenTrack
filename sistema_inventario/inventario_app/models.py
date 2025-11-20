from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class MovimientoInventario(models.Model):
    TIPO_CHOICES = [('E', 'Entrada'), ('S', 'Salida')]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.tipo == 'E':
            self.producto.cantidad += self.cantidad
        elif self.tipo == 'S':
            self.producto.cantidad -= self.cantidad
        self.producto.save()
        super().save(*args, **kwargs)