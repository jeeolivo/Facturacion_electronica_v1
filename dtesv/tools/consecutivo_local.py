from venv import logger
#import pyodbc
from dtesv.models import Parametros
from .sqlQuery import Query  # Asegúrate de importar correctamente tu módulo de consultas SQL

class ConsecutivosSF:
    def __init__(self, tipo_doc, parametros=None, sucursal='0'):
        self.tipo_doc = tipo_doc
        self.parametros = parametros
        self.sucursal = sucursal
        self.query = Query(args=None)  # Inicializa la instancia de Query

    def get(self):
        try:
            result = self.query.ejecutar_procedimiento('MH.ObtenerConsecutivo', self.tipo_doc, self.sucursal)
            if result:
                logger.info(f"Consecutivo obtenido: {result}")
                return {'datos': result}
            else:
                logger.error("No se pudo obtener el consecutivo")
                return {'error': 'No se pudo obtener el consecutivo'}
        except Exception as e:
            logger.error(f"Error inesperado al obtener consecutivo: {e}")
            return {'status': 'RECHAZADO', 'error': "Error inesperado", 'message': str(e)}


    def set(self, nuevo_consecutivo):
        try:
            result = self.query.actualizar_consecutivo('MH.ActualizarConsecutivo', self.tipo_doc, nuevo_consecutivo, self.sucursal)
            if result == 'OK':
                logger.info("Consecutivo actualizado correctamente")
                return {'status': 'OK'}
            else:
                logger.error("No se pudo actualizar el consecutivo")
                return {'status': 'RECHAZADO', 'error': 'No se pudo actualizar el consecutivo'}
        except Exception as e:
            logger.error(f"Error inesperado al actualizar consecutivo: {e}")
            return {'status': 'RECHAZADO', 'error': "Error inesperado", 'message': str(e)}
        
      
        
    def obtener_info_cliente_desde_sqlserver(cliente, empresa_id, factura):
        query = Query(args = None)  # Inicializa la instancia de Query
        # Ejecutamos el procedimiento almacenado
        result = query.cliente_web('MH.ESTRUCTURAR_RECEPTOR_WEB',cliente,empresa_id,factura)

        if result:
                return result
        
        return {}  # En caso de error o sin resultados     