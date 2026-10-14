from dtesv.models import ExtencionEntrega
import logging

logger = logging.getLogger(__name__)


def construir_extension(documentos):

    extra = ExtencionEntrega.objects.filter(id_emisor=documentos.emisor_id.id ).first()
    if not extra:
        return None

    return {
        # 169
        "nombEntrega": extra.nombre if extra.nombre else None,
        # 170
        "docuEntrega": extra.docuentrega if extra.docuentrega else None,
        # 171 "codEmpleado": Aplica a DCLE
        
        # Otros campos de uso interno
        "nombRecibe": None,
        "docuRecibe": None,
        "observaciones": None,
        "placaVehiculo": extra.placa_vehiculo if extra.placa_vehiculo else None
    }