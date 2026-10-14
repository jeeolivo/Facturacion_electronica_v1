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
class get_dte_firma ():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros

    def get_firma(self):   
        logger.info("Ingresando al proceso de firmador")   
        TIMEOUT = 1000
        try:     
            args_json = json.dumps(self.args, cls=DecimalEncoder)
            args_dic =  json.loads(args_json)
            if self.parametros :
                if self.parametros.url_firmador:
                    API_ENDPOINT =self.parametros.url_firmador
                    response = requests.post(API_ENDPOINT,json=args_dic,timeout=TIMEOUT,headers={'content-type': 'application/json'})
                    #logger.error(f"Respuesta del firmador: {response}",exc_info=True)
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
        
        #logger.error(f"Resultado JSON del firmador: {result_js}",exc_info=True)
        return result_js
    
    