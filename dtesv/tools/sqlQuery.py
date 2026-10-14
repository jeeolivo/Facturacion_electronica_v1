from venv import logger
import pyodbc
from .xmlread import xmlread as xmlr
from .conexion import conexion_class as con
from .sqlHelper import DB as sqlhelp

class Query:
    def __init__(self, args):
        self.args = args
        self.connection = con.conexion('default')  # Inicializar la conexión en el constructor
        if not self.connection:
            raise RuntimeError("No se pudo establecer la conexión a la base de datos.")
    
    def fetch_data(self, query, params=None):
        list_result = []
        try:
            if params:
                query_result = sqlhelp(self.connection).select(query, params)
            else:
                xml = xmlr.read_xml()
                query_result = sqlhelp(self.connection).select(xml['queries'][query])

            if query_result:
                columns = [column[0] for column in query_result.description]
                for row in query_result:
                    list_result.append(dict(zip(columns, row)))
        except Exception as e:
            print(f"Error al ejecutar fetch_data: {str(e)}")

        return list_result

    def fetch_data_procedure(self, procedure_name, params=None, whitoutput=None):
        try:
            if params:
                if whitoutput:
                    query = f"EXEC {procedure_name} @tipo_doc = ?, @cod_sucursal = ?, @sig_consec = ? OUTPUT"
                    query_result = sqlhelp(self.connection).select(query, params)
                    return query_result  # Devuelve el resultado completo
                else:
                    query = f"EXEC {procedure_name} {', '.join(['?' for _ in params])}"
                    query_result = sqlhelp(self.connection).select(query, params)
                    return query_result  # Devuelve el resultado completo
            else:
                query_result = sqlhelp(self.connection).select(f"EXEC {procedure_name}")
                return query_result  # Devuelve el resultado completo
        except Exception as e:
            print(f"Error al ejecutar fetch_data_procedure: {str(e)}")
            return None

    def ejecutar_procedimiento(self, nombre_procedimiento, tipo_doc, cod_sucursal):
        try:
            cursor = self.connection.cursor()
            query = f"""
            DECLARE @sig_consec INT;
            EXEC {nombre_procedimiento} @tipo_doc = ?, @cod_sucursal = ?, @sig_consec = @sig_consec OUTPUT;
            SELECT @sig_consec;
            """
            cursor.execute(query, (tipo_doc, cod_sucursal,))
            consecutivo = cursor.fetchone()[0]
            sig_consec = str(consecutivo).zfill(15)
            return sig_consec
        except pyodbc.Error as e:
            print(f"Error al ejecutar el procedimiento almacenado '[MH].[ObtenerConsecutivo]': {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()

    def actualizar_consecutivo(self, nombre_procedimiento, tipo_doc, sig_consec, cod_sucursal):
        cursor = None
        try:
            cursor = self.connection.cursor()
            query = f"""
            DECLARE @msg NVARCHAR(MAX);
            EXEC {nombre_procedimiento} @tipo_doc = ?, @sig_consec = ?, @cod_sucursal = ?, @msg = @msg OUTPUT;
            SELECT @msg;
            """
            cursor.execute(query, (tipo_doc, sig_consec, cod_sucursal))
            msg = cursor.fetchone()[0]
            self.connection.commit()
            logger.info(f"Resultado de la ejecución del SP @msg: {msg}")
            print(f"Resultado de la ejecución del SP @msg: {msg}")
            return msg
        except pyodbc.Error as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"Error al ejecutar el procedimiento almacenado '[MH].[ActualizarConsecutivo]': {e}")
            print(f"Error al ejecutar el procedimiento almacenado '[MH].[ActualizarConsecutivo]': {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if self.connection:
                self.connection.close()


    def cliente_web(self, nombre_procedimiento, cliente, empresa, factura):
        try:
            cursor = self.connection.cursor()
            # Usamos los parámetros correctamente al ejecutar el procedimiento
            query = f"""
                EXEC {nombre_procedimiento} @cliente = ?, @empresa_id = ?, @factura = ?
            """
            cursor.execute(query, (cliente, empresa, factura))
            
            # Obtenemos los resultados
            result = cursor.fetchall()

            # Depuración: Imprimir el resultado de la consulta para ver los datos
            #print("Resultado de la consulta:", result)

            if result:
                    return {
                    'codigo': result[0][0],  # 'codigo' está en la primera posición de la tupla
                    'tipoDocumento': result[0][2],  # 'tipoDocumento' está en la tercera posición de la tupla
                    'numDocumento': result[0][3],  # 'numDocumento' está en la cuarta posición de la tupla
                    'nrc': result[0][4],  # 'nrc' está en la quinta posición de la tupla
                    'nombre': result[0][5],  # 'nombre' está en la sexta posición de la tupla
                    'codActividad': {result[0][7]}, # 'codActividad'
                    'actividad_economica': f"{result[0][7]}:{result[0][6]}",  # 'codActividad' y 'descActividad'
                    'nombreComercial': result[0][8],  # 'nombreComercial'
                    'codPais': result[0][14],
                    'tipoPersona': result[0][15],  # 'tipoPersona'
                    'tipoReceptor': result[0][16],  # 'tipoReceptor'
                    'departamento': 'San Salvador', #result[0][13],  # 'departamento'
                    'vendedor': 'V169',
                    'municipio': 'San Salvador', #result[0][18],  # 'municipio'
                    'complemento': result[0][11],  # 'complemento'
                    'telefono': result[0][9],  # 'telefono'
                    'correo': result[0][10],  # 'correo'
                    'incoterms': None,  # Asumiendo que no se ha proporcionado incoterms
                    'rutaEntrega': 'E169',
                    }
            return {}
        except pyodbc.Error as e:
            print(f"Error al ejecutar el procedimiento almacenado '[MH].[ESTRUCTURAR_RECEPTOR_WEB]': {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()                   
