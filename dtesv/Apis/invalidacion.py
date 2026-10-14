
import requests
import json
from requests.exceptions import Timeout,RequestException 
 

# Este metodo envia la Firma y la informacion requerida  a hacienda y retorna el resultado dado por mh

class post_recepciondte ():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros

    def sent_data(self):      
        TIMEOUT = 50
        API_ENDPOINT = self.parametros.url_invalidacion
        result_js = {
            'estado': 'ERROR',
            'descripcionMsg': "Error desconocido en la solicitud",
            'observaciones': "Validar datos del documento",
            'selloRecibido': None
        }  # Inicialización predeterminada

        try:
            auth = self.args['auth']   
            documento = self.args['documento']  
            #API_ENDPOINT = self.parametros.url_invalidacion

            # 2025-01-06: Autenticación y documento
            if not auth or not documento:
                raise ValueError("Faltan datos necesarios: 'auth' o 'documento'")

            tipo_dte = documento.get('identificacion', {}).get('tipoDte')

            response = requests.post(API_ENDPOINT,json=documento,timeout=TIMEOUT,headers={'content-type': 'application/json','Authorization':auth})
            #result_js = response.json()
            
            # 2025-01-06: Validar el código de estado de la respuesta
            if response.status_code in [200, 201, 202]:
                result_js = response.json()
            else:
                # Solo hacer la petición si tipoDte es '03'
                if tipo_dte == '03':
                    result_js = {
                        'estado': 'ERROR',
                        'descripcionMsg': f"Error {response.status_code}: Este documento deber ser invalidado mediante NC o ND según corresponda.",
                        'observaciones': "Este documento deber ser invalidado mediante NC o ND según corresponda.",
                        'selloRecibido': None
                    }
                    
                else:
                    result_js = response.json()
        
        except ValueError as ve:
            result_js = {
                'estado': 'RECHAZADO',
                'descripcionMsg': str(ve),
                'observaciones': "Validar datos del documento",
                'selloRecibido': None
            }
        
        except RequestException as er:
            for ar in er.args:
              if 'No connection' in str(ar) : 
                    respuesta_mh = ({'estado':'RECHAZADO','descripcionMsg':" Error en conexion a endpoint "+API_ENDPOINT ,'observaciones':"endpoint fuera de linea o sin acceso a internet", 'observaciones': "Intente generar otro documento para invalidar",'selloRecibido':None})   
                    result_js = respuesta_mh
        return result_js