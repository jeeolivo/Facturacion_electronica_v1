# utils/diccionario.py

class DiccionarioUtil:

    @staticmethod
    def quitar(diccionario, campos):
        """
        Elimina las llaves indicadas de un diccionario.
        """
        return {
            k: v
            for k, v in diccionario.items()
            if k not in campos
        }

    @staticmethod
    def quitar_lista(lista, campos):
        """
        Aplica quitar() a todos los elementos de una lista de diccionarios.
        """
        return [
            DiccionarioUtil.quitar(item, campos)
            for item in lista
        ]

    @staticmethod
    def agregar_si(diccionario, clave, valor):
        """
        Agrega una llave únicamente cuando el valor no es None.
        """
        if valor is not None:
            diccionario[clave] = valor

        return diccionario

    @staticmethod
    def renombrar(diccionario, origen, destino):
        """
        Cambia el nombre de una llave conservando su valor.
        """
        if origen in diccionario:
            diccionario[destino] = diccionario.pop(origen)

    @staticmethod
    def conservar(diccionario, campos):
        """
        Conserva únicamente las llaves indicadas.
        """
        return {
            k: v
            for k, v in diccionario.items()
            if k in campos
        }

    @staticmethod
    def actualizar(diccionario, datos):
        """
        Actualiza un diccionario ignorando valores None.
        """
        for k, v in datos.items():
            if v is not None:
                diccionario[k] = v

        return diccionario