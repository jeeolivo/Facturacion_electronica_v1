from venv import logger
import requests
import json
from requests.exceptions import Timeout,RequestException 
import decimal
from dtesv.models  import Parametros
 
 

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
#'''Este metodo se conecta al servicio ya sea local o  doker  que se instalo para generar las Firmas  para  ser envias a MH'''
class ConsecutivosSF ():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros

    def get(self):      
        TIMEOUT = 1000
        try:     
            if self.parametros :
                if self.parametros.url_getconsectivoSF:
                    cod_doc = self.args
                    API_ENDPOINT =self.parametros.url_getconsectivoSF+cod_doc
                        # Realizar la solicitud GET
                    response = requests.get(API_ENDPOINT)
                    logger.error(f"Respuesta de solicitud {response}",exc_info=True)

                    # Verificar si la solicitud fue exitosa (código 200)
                    if response.status_code == 200:
                        # Obtener los datos en formato JSON
                        result_js = response.json()
                        # Imprimir el consecutivo obtenido
                        
                    else:
                        # Manejar errores si la solicitud no fue exitosa
                        result_js = ('Error al obtener el consecutivo. Código de respuesta:', response.status_code)

        except Exception as er:
            for ar in er.args:
              respuesta_mh = ({'status':'RECHAZADO','error':" Error en conexion a endpoint ",'path':API_ENDPOINT ,'message':str(ar)})   
              result_js = respuesta_mh
        return result_js
    
    def set(self):      
        TIMEOUT = 1000
        try:
            cod_doc = self.args[0]     
            args_json = json.dumps(self.args[1], cls=DecimalEncoder)
            args_dic =  json.loads(args_json)
            if self.parametros :
                if self.parametros.url_setconsectivoSF:
                    API_ENDPOINT =self.parametros.url_setconsectivoSF+cod_doc
                    response = requests.post(API_ENDPOINT,json=args_dic,timeout=TIMEOUT,headers={'content-type': 'application/json'})
                    result_js = response.json()
                else:
                    result_js = ({'status':'RECHAZADO','error':" Error en conexion a endpoint ",'path':"No Establecido" ,'message':"endpoint  No establecido"})   
            else:
                result_js = ({'status':'ERROR','error':" Error en conexion a endpoint ",'path':"No Establecido" ,'message':"Parametros para la empresa No establecidos"})   
        #except RequestException as er:
        except Exception as er:
            for ar in er.args:
              respuesta_mh = ({'status':'RECHAZADO','error':" Error en conexion a endpoint ",'path':API_ENDPOINT ,'message':str(ar)})   
              result_js = respuesta_mh
        return result_js
    
    