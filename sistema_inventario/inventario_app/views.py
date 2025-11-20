from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from django.db import models
from .models import Producto, MovimientoInventario, Categoria

from .forms import ProductoForm, MovimientoForm
from django.contrib.auth.decorators import login_required

# Vista para crear un nuevo producto
@login_required
def producto_nuevo(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario_app/producto_form.html', {'form': form, 'nuevo': True})

@login_required
def movimiento_nuevo(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.usuario = request.user
            mov.save()
            return redirect('movimientos')
    else:
        form = MovimientoForm()
    return render(request, 'inventario_app/movimiento_form.html', {'form': form})

@login_required
def movimientos_exportar(request):
    qs = MovimientoInventario.objects.select_related('producto', 'usuario').all().order_by('-fecha')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="movimientos.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Fecha', 'Producto', 'Código', 'Tipo', 'Cantidad', 'Usuario', 'Observación'])
    for mov in qs:
        writer.writerow([
            mov.id,
            mov.fecha.strftime('%Y-%m-%d %H:%M'),
            mov.producto.nombre,
            mov.producto.codigo,
            dict(MovimientoInventario.TIPO_CHOICES).get(mov.tipo, mov.tipo),
            mov.cantidad,
            mov.usuario.get_full_name() or mov.usuario.username,
            mov.observacion or '',
        ])
    return response
# Editar producto
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario_app/producto_form.html', {'form': form, 'nuevo': False})

# Eliminar producto
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos')
    return render(request, 'inventario_app/producto_confirmar_eliminar.html', {'producto': producto})

from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import Producto, MovimientoInventario

def index(request):
        # Estadísticas generales
    total_productos = Producto.objects.count()
    
    # Valor total del inventario (precio_compra * cantidad)
    valor_inventario = Producto.objects.aggregate(
        total=Sum(F('precio_compra') * F('cantidad'))
    )['total'] or 0
    
    # Productos con stock bajo (menos de 10 unidades)
    stock_bajo = Producto.objects.filter(cantidad__lt=10).count()
    
    # Movimientos de hoy
    hoy = timezone.now().date()
    movimientos_hoy = MovimientoInventario.objects.filter(
        fecha__date=hoy
    ).count()
    
    # Movimientos recientes (últimos 5)
    movimientos_recientes = MovimientoInventario.objects.select_related(
        'producto', 'usuario'
    ).order_by('-fecha')[:5]
    
    # Datos para gráfico de movimientos del mes (últimos 30 días)
    hace_30_dias = timezone.now() - timedelta(days=30)
    movimientos_mes = MovimientoInventario.objects.filter(
        fecha__gte=hace_30_dias
    ).extra(
        select={'dia': 'DATE(fecha)'}
    ).values('dia').annotate(
        entradas=Count('id', filter=models.Q(tipo='E')),
        salidas=Count('id', filter=models.Q(tipo='S'))
    ).order_by('dia')
    
    # Formatear datos para Chart.js
    fechas = [mov['dia'].strftime('%d/%m') for mov in movimientos_mes]
    entradas = [mov['entradas'] for mov in movimientos_mes]
    salidas = [mov['salidas'] for mov in movimientos_mes]
    
    # Datos para gráfico de categorías
    productos_categoria = Categoria.objects.annotate(
        total=Count('producto')
    ).values('nombre', 'total').order_by('-total')
    
    categorias = [cat['nombre'] for cat in productos_categoria]
    cantidades_cat = [cat['total'] for cat in productos_categoria]
    
    context = {
        'total_productos': total_productos,
        'valor_inventario': round(valor_inventario, 2),
        'stock_bajo': stock_bajo,
        'movimientos_hoy': movimientos_hoy,
        'movimientos_recientes': movimientos_recientes,
        'fechas': fechas,
        'entradas': entradas,
        'salidas': salidas,
        'categorias': categorias,
        'cantidades_cat': cantidades_cat,
    }
    
    return render(request, 'inventario_app/index.html', context)


from django.core.paginator import Paginator
from django.db.models import Q

def productos(request):
    qs = Producto.objects.select_related('categoria').all()
    search = request.GET.get('search', '').strip()
    categoria = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')
    page = request.GET.get('page', 1)

    # Filtro de búsqueda
    if search:
        qs = qs.filter(Q(nombre__icontains=search) | Q(codigo__icontains=search))

    # Filtro de categoría
    if categoria and categoria != '':
        qs = qs.filter(categoria__nombre=categoria)

    # Filtro de estado de stock
    if estado == 'En stock':
        qs = qs.filter(cantidad__gt=20)
    elif estado == 'Stock bajo':
        qs = qs.filter(cantidad__gt=0, cantidad__lte=20)
    elif estado == 'Sin stock':
        qs = qs.filter(cantidad__lte=0)

    paginator = Paginator(qs, 10)
    productos_page = paginator.get_page(page)

    # Para el select de categorías
    categorias = list(set(Producto.objects.values_list('categoria__nombre', flat=True)))
    categorias.sort()

    return render(request, 'inventario_app/productos.html', {
        'productos': productos_page,
        'categorias': categorias,
        'search': search,
        'categoria_selected': categoria,
        'estado_selected': estado,
        'paginator': paginator,
        'page_obj': productos_page,
    })

from datetime import datetime, timedelta

def movimientos(request):
    qs = MovimientoInventario.objects.select_related('producto', 'usuario').all().order_by('-fecha')
    search = request.GET.get('search', '').strip()
    tipo = request.GET.get('tipo', '')
    fecha = request.GET.get('fecha', '')
    page = request.GET.get('page', 1)

    # Filtro de búsqueda (producto nombre o código)
    if search:
        qs = qs.filter(
            Q(producto__nombre__icontains=search) | Q(producto__codigo__icontains=search)
        )

    # Filtro de tipo
    if tipo and tipo != '':
        if tipo == 'Entrada':
            qs = qs.filter(tipo='E')
        elif tipo == 'Salida':
            qs = qs.filter(tipo='S')
        elif tipo == 'Ajuste':
            qs = qs.filter(observacion__icontains='ajuste')

    # Filtro de fecha
    if fecha == 'Hoy':
        today = datetime.now().date()
        qs = qs.filter(fecha__date=today)
    elif fecha == 'Últimos 7 días':
        start = datetime.now().date() - timedelta(days=7)
        qs = qs.filter(fecha__date__gte=start)
    elif fecha == 'Últimos 30 días':
        start = datetime.now().date() - timedelta(days=30)
        qs = qs.filter(fecha__date__gte=start)
    elif fecha == 'Este mes':
        now = datetime.now()
        qs = qs.filter(fecha__year=now.year, fecha__month=now.month)

    paginator = Paginator(qs, 10)
    movimientos_page = paginator.get_page(page)
    
    #n° entradas
    for mov in movimientos_page:
        mov.numero_entradas = MovimientoInventario.objects.filter(producto=mov.producto, tipo='E').count()
        
    #n° salidas
    for mov in movimientos_page:
        mov.numero_salidas = MovimientoInventario.objects.filter(producto=mov.producto, tipo='S').count()
    
    #n° ajustes
    for mov in movimientos_page:
        mov.numero_ajustes = MovimientoInventario.objects.filter(producto=mov.producto, observacion__icontains='Ajuste').count()
        
    #n° movimientos total
    for mov in movimientos_page:
        mov.numero_movimientos = MovimientoInventario.objects.all().filter(producto=mov.producto).count()
        
    #stock anterior y nuevo
    for mov in movimientos_page:
        mov.stock_anterior = mov.producto.cantidad
        mov.stock_nuevo = mov.stock_anterior + mov.cantidad if mov.tipo == 'E' else mov.stock_anterior - mov.cantidad

    return render(request, 'inventario_app/movimientos.html', {
        'movimientos': movimientos_page,
        'search': search,
        'tipo_selected': tipo,
        'fecha_selected': fecha,
        'paginator': paginator,
        'page_obj': movimientos_page,
        'numero_entradas': mov.numero_entradas,
        'numero_salidas': mov.numero_salidas,
        'numero_ajustes': mov.numero_ajustes,
        'numero_movimientos': mov.numero_movimientos,
        'stock_anterior': mov.stock_anterior,
        'stock_nuevo': mov.stock_nuevo,
    })