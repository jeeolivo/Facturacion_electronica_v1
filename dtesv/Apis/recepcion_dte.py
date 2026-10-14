import requests
import json
from requests.exceptions import Timeout,RequestException 
import logging
logger = logging.getLogger(__name__)
import traceback


# Este metodo envia la Firma y la informacion requerida  a hacienda y retorna el resultado dado por mh
MH_HEADERS_BASE = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0',
}

class post_recepciondte ():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros
    def sent_data(self):
        TIMEOUT = 50
        API_ENDPOINT = self.parametros.url_dte   # en consulta, la URL de consulta
        try:
            response = requests.post(
                API_ENDPOINT, json=self.args['documento'], timeout=TIMEOUT,
                headers={**MH_HEADERS_BASE,
                        'Authorization': self.args['auth']})
        except RequestException as er:
            logger.error("Error de conexión a MH (%s): %s", API_ENDPOINT, er, exc_info=True)
            return {'estado': 'ERROR_CONEXION', 'descripcionMsg': str(er),
                    'observaciones': [], 'selloRecibido': None}

        try:
            return response.json()
        except ValueError:
            logger.error("MH respondió sin JSON. status=%s body=%r",
                        response.status_code, response.text[:500])
            return {'estado': 'ERROR_RESPUESTA',
                    'descripcionMsg': f'HTTP {response.status_code} sin JSON',
                    'observaciones': [], 'selloRecibido': None}              
        # TIMEOUT = 50
        # result_js = {}
        # try:
        #     auth = self.args['auth']   
        #     documento = self.args['documento']  
        #     API_ENDPOINT = self.parametros.url_dte
        #     response = requests.post(API_ENDPOINT,json=documento,timeout=TIMEOUT,headers={'content-type': 'application/json','Authorization':auth})
        #     result_js = response.json()
        # except RequestException as er:
        #     for ar in er.args:
        #       if 'No connection' in str(ar) : 
        #             respuesta_mh = ({'status':'RECHAZADO','descripcionMsg':" Error en conexion a endpoint "+API_ENDPOINT ,'observaciones':"endpoint  fuera de linea o sin  acceso a internet",'selloRecibido':None})   
        #             result_js = respuesta_mh
        # return result_js

class post_recepcioncontingencia ():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros
    def sent_data(self):      
        TIMEOUT = 50
        try:
            auth = self.args['auth']   
            documento = self.args['documento']  
            API_ENDPOINT = self.parametros.url_contingencia
            response = requests.post(API_ENDPOINT,json=documento,timeout=TIMEOUT,headers={'content-type': 'application/json','Authorization':auth})
            result_js = response.json()
        except RequestException as er:
            for ar in er.args:
              if 'No connection' in str(ar) : 
                    respuesta_mh = ({'status':'RECHAZADO','descripcionMsg':" Error en conexion a endpoint "+API_ENDPOINT ,'observaciones':"endpoint  fuera de linea o sin  acceso a internet",'selloRecibido':None})   
                    result_js = respuesta_mh
        return result_js
    

class post_recepciondteLote ():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros
    def sent_data(self):      
        TIMEOUT = 50
        try:
            auth = self.args['auth']   
            documento = self.args['documento']  
            API_ENDPOINT = self.parametros.url_dte_lote
            response = requests.post(API_ENDPOINT,json=documento,timeout=TIMEOUT,headers={'content-type': 'application/json','Authorization':auth})
            result_js = response.json()
        except RequestException as er:
            for ar in er.args:
              if 'No connection' in str(ar) : 
                    respuesta_mh = ({'status':'RECHAZADO','descripcionMsg':" Error en conexion a endpoint "+API_ENDPOINT ,'observaciones':"endpoint  fuera de linea o sin  acceso a internet",'selloRecibido':None})   
                    result_js = respuesta_mh
        return result_js

class get_documentosLote():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros
    def sent_data(self):      
        TIMEOUT = 50
        try:
            auth = self.args['auth']
            loteId = self.args['loteId']
            API_ENDPOINT = self.parametros.url_dte_lote_consulta +loteId
            response = requests.get(API_ENDPOINT,timeout=TIMEOUT,headers={'content-type': 'application/json','Authorization':auth})
            result_js = response.json()
        except RequestException as er:
            for ar in er.args:
              if 'No connection' in str(ar) : 
                    respuesta_mh = ({'status':'RECHAZADO','descripcionMsg':" Error en conexion a endpoint "+API_ENDPOINT ,'observaciones':"endpoint  fuera de linea o sin  acceso a internet",'selloRecibido':None})   
                    result_js = respuesta_mh
        return result_js

# class post_consultadte ():
#     def __init__(self,args,parametros):
#         self.args = args
#         self.parametros = parametros

#     def sent_data(self):      
#         TIMEOUT = 50
#         result_js = None  # Inicializar la variable antes del bloque try
#         try:
#             auth = self.args['auth']   
#             documento = self.args['documento']  
#             API_ENDPOINT = self.parametros.url_dte_consulta #+'/'+ documento['codigoGeneracion']
#             response = requests.post(API_ENDPOINT,json=documento,timeout=TIMEOUT,headers={'content-type': 'application/json','Authorization':auth})
#             #response= requests.get(API_ENDPOINT,headers={'content-type': 'application/json','Authorization':auth})            
#             logger.error(f" datos: {response.json()},{documento}", exc_info=True)
#             # traceback.print_exc()  
#             # result_js = response.json()
#                         # Verificar el código de estado antes de intentar acceder a response.json()
#             if response.status_code in [200, 201, 202]:
#                 result_js = response.json()
#             else:
#                 logger.error(f"Error: respuesta inesperada con estado {response.status_code}")
#                 result_js = {'status': 'ERROR', 'descripcionMsg': f"Error {response.status_code}: Unauthorized acceso al endpoint"}

#             logger.error(f"datos: {result_js},{documento}", exc_info=True)

#         except RequestException as er:
#             for ar in er.args:
#               if 'No connection' in str(ar) : 
#                     respuesta_mh = ({'status':'RECHAZADO','descripcionMsg':" Error en conexion a endpoint "+API_ENDPOINT ,'observaciones':"endpoint  fuera de linea o sin  acceso a internet",'selloRecibido':None})   
#                     result_js = respuesta_mh
#             logger.error("Excepción de conexión a la API", exc_info=True)
        
#         # Devolver un mensaje de error si result_js sigue siendo None
#         if result_js is None:
#             result_js = {'status': 'ERROR', 'descripcionMsg': "Error desconocido en la solicitud"}
        
#         return result_js

class post_consultadte():
    def __init__(self, args, parametros):
        self.args = args
        self.parametros = parametros

    @staticmethod
    def _error(estado, descripcion, **extra):
        # Misma forma que la respuesta exitosa: siempre trae 'estado'
        resp = {'estado': estado, 'descripcionMsg': descripcion,
                'selloRecibido': None, 'observaciones': []}
        resp.update(extra)
        return resp

    def sent_data(self):
        TIMEOUT = 50
        API_ENDPOINT = self.parametros.url_dte_consulta
        documento = self.args['documento']

        try:
            response = requests.post(
                API_ENDPOINT, json=documento, timeout=TIMEOUT,
                headers={**MH_HEADERS_BASE,
                         'Authorization': self.args['auth']})
        except RequestException as er:
            logger.error("Consulta MH: error de conexión a %s: %s",
                         API_ENDPOINT, er, exc_info=True)
            return self._error('ERROR_CONEXION',
                               f"Error de conexión a {API_ENDPOINT}: {er}")

        # Parsear sin reventar si el cuerpo no es JSON
        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code in (200, 201, 202) and isinstance(data, dict):
            logger.info("Consulta MH %s -> %s", documento.get('codigoGeneracion'),
                        data.get('estado'))
            return data

        logger.error("Consulta MH falló. status=%s codigoGeneracion=%s body=%r",
                     response.status_code, documento.get('codigoGeneracion'),
                     response.text[:500])
        return self._error('ERROR_CONSULTA',
                           f"HTTP {response.status_code} en consulta a MH",
                           httpStatus=response.status_code,
                           detalle=data if data is not None else response.text[:500])