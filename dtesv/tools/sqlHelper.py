from .conexion import conexion_class as con

class DB:
    def __init__(self, connection):
        self.connection = connection

    def select(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            list_result = [dict(zip(columns, row)) for row in result]

            cursor.close()
            return list_result
        except Exception as e:
            print(f"Error al ejecutar la consulta: {str(e)}")
            return None
