import json
import jsonschema 
from decimal import Decimal
import sys
import os
from jsonschema.exceptions import ValidationError, ErrorTree



current_directory = os.path.dirname(os.path.abspath(__file__))
directorio_actual = os.getcwd()
mymodule_dir = os.path.join( directorio_actual, 'dtesv' )
schema_dir = os.path.join( mymodule_dir, 'schemas' )


class schemaValidate():
    def __init__(self, args):
        self.args = args
        
    def validar_schema(self):
       
        # resivo el nombre del schema segun el tipo de documento 
        tipo_documento = self.args['tipo']
        # resivo el json a validar este realmente es un dicionario 
        jsonaValidar =self.args['json']
        direccion_schema = schema_dir+'/'+tipo_documento+'.json'
        with open(direccion_schema, 'r') as f:
            schema = json.load(f)

        # genero un metodo lambda que removera todos las propiedades   multipleOf   hago esto por que  para el caso de los redondeos
        # de los float que son los datos que  acepta JSON  tienen problemas de redonde  entonces para evitar ese tipo de error y como lo 
        # que me interesa es solo validar que todos los vampos requeridos  esten en el Json generado por la aplicacion 
        remove_multiple_of = lambda x: (isinstance(x, dict) and {k: remove_multiple_of(v) for k, v in x.items() if k != 'multipleOf'}) or (isinstance(x, list) and [remove_multiple_of(i) for i in x]) or x

        #genero un nuevo diccionario sin las propiedades multipleOf desde el schema original
        schema_without_multiple_of = remove_multiple_of(schema)
       
       # hago la comprobacion que el Json generado por la App cumpla con el schema dado por  MH  
        try:  
           resultado =  jsonschema.validate(jsonaValidar,schema_without_multiple_of)   

           if not resultado :
               
               return True
           
           return False
           
        except ValidationError  as err:            
            validacion_error = 'Error En:'+err.json_path+' '+'Error:'+err.message
            return  validacion_error
           
        
    def get_schema(self):       
        tipo_documento = self.args['tipo']
              # resivo el json a validar este realmente es un dicionario 
        ruta_json = os.path.join(schema_dir, tipo_documento+".json")
        with open(ruta_json, 'r') as f:
            schema = json.load(f)

        return schema
    
    def validate_schema_receptor(self):
        ruta_json = os.path.join(schema_dir, "fe-fc-v1.json")
        with open(ruta_json, 'r') as f:
            schema = json.load(f)
        jsonaValidar =self.args['json']
        receptor_schema = schema['properties']['receptor']
        remove_multiple_of = lambda x: (isinstance(x, dict) and {k: remove_multiple_of(v) for k, v in x.items() if k != 'multipleOf'}) or (isinstance(x, list) and [remove_multiple_of(i) for i in x]) or x
        schema_without_multiple_of = remove_multiple_of(receptor_schema)
        try:  
           resultado =  jsonschema.validate(jsonaValidar,schema_without_multiple_of)         
           if not resultado :
               return True
           
           return False
           
        except ValidationError  as err:            
                validacion_error = 'Error En:'+err.json_path+' '+'Error:'+err.message
                return  validacion_error
