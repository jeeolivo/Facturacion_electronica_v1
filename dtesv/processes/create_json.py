
import json
from decimal import Decimal
from datetime import date, datetime ,time
import os
from dtesv.models  import Parametros,Documentos,Company
import logging
import traceback

current_directory = os.path.dirname(os.path.abspath(__file__))
directorio_actual = os.getcwd()
mymodule_dir = os.path.join(directorio_actual, 'Facturacion_electronica\\dtesv')
#Documentos_json_dir =os.path.join(mymodule_dir, 'documentos\json\\')
logger = logging.getLogger(__name__)

class fakefloat(float):
    def __init__(self, value):
        self._value = value
        
    def __repr__(self):
        return str(self._value)


class gen_json():
    def __init__(self, args):
        self.args = args
                
        
    def defaultencode(o):
        if isinstance(o, Decimal):
        # Subclass float with custom repr?
            return fakefloat(o)
        elif  isinstance(o, (datetime, date, time)):
                return o.isoformat()  
        raise TypeError(repr(o) + " is not JSON serializable")        

    def create_fileJson(self, datas, parametros):
        try:
            if not parametros:
                logger.error("[CREATE_JSON] No se recibieron parámetros de la empresa.")
                return None

            if not parametros.attachment_files_path:
                logger.error("[CREATE_JSON] La empresa no tiene attachment_files_path configurado.")
                return None

            codigoGeneracion = datas["identificacion"]["codigoGeneracion"]

            dirercion_js_save = parametros.attachment_files_path

            direccion_documento_js = os.path.join(
                dirercion_js_save,
                f"{codigoGeneracion}.json"
            )

            with open(direccion_documento_js, "w", encoding="utf-8") as outfile:
                json.dump(
                    datas,
                    outfile,
                    indent=4,
                    ensure_ascii=False,
                    default=gen_json.defaultencode
                )

            logger.info(
                f"[CREATE_JSON] JSON creado correctamente: {direccion_documento_js}"
            )

            return direccion_documento_js

        except Exception as e:
            logger.error(
                f"[CREATE_JSON] Error creando JSON: {e}",
                exc_info=True
            )
            return None
        
    def write_fileJSon(self,datosUpdate):
        parametros = Parametros.objects.filter(
        company_id=Company.objects.get(id=1)).first()
        if parametros.attachment_files_path:
            dirercion_js_save =parametros.attachment_files_path
            nombre_archivo = f"{datosUpdate.codigoGeneracion}.json"
            # Verificar si el archivo existe
            if os.path.exists(dirercion_js_save+nombre_archivo):
                # Leer el contenido actual del archivo JSON
                try:
                    with open(dirercion_js_save+nombre_archivo, 'r') as file:
                        contenido = json.load(file)

                        # Modificar el contenido según los datos a editar
                   
                    contenido['identificacion']['FechaAnulacion'] = datosUpdate.fecha_anula_mh
                    contenido['identificacion']['selloInvalidacion'] = datosUpdate.selloInvalidacion
                    contenido['identificacion']['motivoInvalidacion'] = datosUpdate.motivoInvalidacion

                            

                    # Escribir el contenido modificado de vuelta al archivo JSON
                    with open(dirercion_js_save+nombre_archivo, 'w') as file:
                        json.dump(contenido, file, indent=4, ensure_ascii=False,default=gen_json.defaultencode)

                    logger.error(file, exc_info=True)
                    traceback.print_exc()    
                except Exception as e:  
                    logger.error(f"Error in createJsonInvalid: {e}", exc_info=True)
                    traceback.print_exc()        
        
    def save_fileJSon(self,datosUpdate):
            parametros = Parametros.objects.filter(
            company_id=Company.objects.get(id=1)
                 ).first()
            if parametros.attachment_files_path:
                dirercion_js_save =parametros.attachment_files_path
                
                 
            # Verificar si el archivo existe
               
                try:
                    nombre_archivo = datosUpdate['dteJson']['documento']['codigoGeneracion']+'.json'                    
                    with open(dirercion_js_save+'invalid_'+nombre_archivo, 'w') as outfile:
                            json.dump(datosUpdate, outfile, indent=4, ensure_ascii=False,default=gen_json.defaultencode)
                except Exception as e:  
                    logger.error(f"Error in createJsonInvalid: {e}", exc_info=True)
                    traceback.print_exc()        
        
    def create_fileJSonLocal(self,datosUpdate):
          
            parametros = Parametros.objects.filter(
            company_id=Company.objects.get(id=1)
                 ).first()
            if parametros.attachment_files_path:
                dirercion_js_save =parametros.attachment_files_path
                
                 
            # Verificar si el archivo existe
               
                try:
                    nombre_archivo = datosUpdate['dic_dte']['identificacion']['codigoGeneracion']+'.json'                    
                    with open(dirercion_js_save+'debug_'+nombre_archivo, 'w') as outfile:
                            json.dump(datosUpdate, outfile, indent=4, ensure_ascii=False,default=gen_json.defaultencode)
                except Exception as e:  
                    logger.error(f"Error in createJsondebug: {e}", exc_info=True)
                    traceback.print_exc()        
        