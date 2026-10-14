import requests
import json
from requests.exceptions import Timeout,RequestException 
import logging
import traceback
logger = logging.getLogger(__name__)
 


# Este Metodo me autentifica  con hacienda y me retorna el token para envio de infomacion a  MH
class authenticate ():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros
    def get_token(self):      
        TIMEOUT = 50
        try:     
            #logger.error(f"respuesta_mh: {str(self.args)}", exc_info=True)
            #traceback.print_exc() 
            API_ENDPOINT = self.parametros.url_autentication
            response = requests.post(API_ENDPOINT,data=self.args,timeout=TIMEOUT,headers={'content-type': 'application/x-www-form-urlencoded'})
            result_js = response.json()
           # print(result_js)
           # logger.error(f"respuesta_mh: {result_js}", exc_info=True)
           # traceback.print_exc()
        except RequestException as er:
            for ar in er.args:
              if 'No connection' in str(ar) : 
                    respuesta_mh = ({'status':'RECHAZADO','descripcionMsg':" Error en conexion a endpoint "+API_ENDPOINT ,'observaciones':"endpoint  fuera de linea o sin  acceso a internet",'selloRecibido':None,'estado':'ERROR'
                                     ,'cadena': "Error en conexion a endpoint "+API_ENDPOINT})   
                    result_js = respuesta_mh
              else:
                   respuesta_mh = ({'status':'RECHAZADO','descripcionMsg':" Error en conexion a endpoint "+API_ENDPOINT ,'observaciones':"endpoint  fuera de linea o sin  acceso a internet",'selloRecibido':None,'estado':'ERROR'
                                    ,'cadena': "Error en conexion a endpoint "+API_ENDPOINT})       
                   result_js = respuesta_mh
            #print(result_js)
            #logger.error(f"respuesta_mh: {result_js}", exc_info=True)
            #traceback.print_exc()
            
       # except Exception as e:
       #     logger.error(f"respuesta_mh: {str(e)}", exc_info=True)
       #     traceback.print_exc()
        return result_js