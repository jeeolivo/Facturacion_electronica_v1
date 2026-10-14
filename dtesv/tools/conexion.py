import pyodbc
from django.conf import settings

class conexion_class:
    @staticmethod
    def conexion(database_name):
        try:
            connection = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={settings.DATABASES[database_name]['HOST']};"
                f"PORT={settings.DATABASES[database_name]['PORT']};"
                f"DATABASE={settings.DATABASES[database_name]['NAME']};"
                f"UID={settings.DATABASES[database_name]['USER']};"
                f"PWD={settings.DATABASES[database_name]['PASSWORD']}"
            )
            return connection
        except Exception as e:
            print(f"Error al establecer la conexión a la base de datos: {str(e)}")
            return None