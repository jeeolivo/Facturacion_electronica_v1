import requests
import json
from requests.exceptions import Timeout,RequestException 
import decimal
from dtesv.models  import Parametros
import locale
 
 

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
           # valornew = round(float(obj),2)
            formatted_value = locale.format_string('%.2f', float(obj), grouping=True)
            return formatted_value
        return super(DecimalEncoder, self).default(obj)
#'''Este metodo se conecta al servicio ya sea local o  doker  que se instalo para generar las Firmas  para  ser envias a MH'''
class sentEmail ():
    def __init__(self,args,parametros):
         
        self.args = args
        self.parametros = parametros

    def sent(self): 
        locale.setlocale(locale.LC_NUMERIC, 'es_SV.UTF-8')     
        TIMEOUT = 50
        try:     
            args_json = json.dumps(self.args, cls=DecimalEncoder)
            args_dic =  json.loads(args_json)
            
            if self.parametros :
                if self.parametros.url_email_api:
                    API_ENDPOINT =self.parametros.url_email_api
                    toke_id = self.ger_token(self.parametros)

                    response = requests.post(API_ENDPOINT,json=args_dic,timeout=TIMEOUT,headers={'content-type': 'application/json','Authorization':'bearer '+toke_id['token'] })
                    result_js = response.json()
                else:
                    result_js = ({'status':'ERROR','error':" Error en conexion a endpoint ",'path':"No Establecido" ,'message':"endpoint  No establecido"})   
            else:
                result_js = ({'status':'ERROR','error':" Error en conexion a endpoint ",'path':"No Establecido" ,'message':"Parametros para la empresa No establecidos"})   
        #except RequestException as er:
        except Exception as er:
            for ar in er.args:
              respuesta_mh = ({'status':'RECHAZADO','error':" Error en conexion a endpoint ",'path':API_ENDPOINT ,'message':str(er)})   
              result_js = respuesta_mh
        return result_js
    
    def ger_token(self,params):
        TIMEOUT = 50
        try:
            user_dic = {'id':params.user_login_email,'pw':params.pass_login_email}
            args_json = json.dumps(user_dic)
            args_dic =  json.loads(args_json)
                
            if params :
                if params.url_email_api_login:
                    API_ENDPOINT =params.url_email_api_login
                    response = requests.post(API_ENDPOINT,json=args_dic,timeout=TIMEOUT)
                    result_js = response.json()
                else:
                    result_js = ({'status':'ERROR','error':" Error en conexion a endpoint ",'path':"No Establecido" ,'message':"endpoint  No establecido"})   
            else:
                result_js = ({'status':'ERROR','error':" Error en conexion a endpoint ",'path':"No Establecido" ,'message':"Parametros para la empresa No establecidos"})   
        #except RequestException as er:
        except Exception as er:
                for ar in er.args:
                    respuesta_mh = ({'status':'RECHAZADO','error':" Error en conexion a endpoint ",'path':API_ENDPOINT ,'message':str(ar)})   
                result_js = respuesta_mh
        return result_js
            
    
