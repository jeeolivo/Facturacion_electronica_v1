from django.http import JsonResponse

from dtesv.models import Receptor, Proveedor

def get_email_counts(request):
    email = 'efactura@lamorazan.com'
    
    receptores_count = Receptor.objects.filter(correo=email).count()
    proveedores_count = Proveedor.objects.filter(correo=email).count()
    
    return JsonResponse({
        'receptores_count': receptores_count,
        'proveedores_count': proveedores_count,
    })