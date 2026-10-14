import json
import logging
import dtesv.processes.validate_schema as validateSchema
from pathlib import Path
from dtesv.models import C002TipoDocumento

logger = logging.getLogger(__name__)

class SchemaHelper:

    @classmethod
    def limpiar_none(cls, data, requeridos, ruta_actual=""):
        """
        Elimina únicamente los campos opcionales cuyo valor sea None.
        Conserva los campos requeridos definidos en el JSON Schema.
        """

        if isinstance(data, dict):
            resultado = {}
            required = requeridos.get(ruta_actual, set())

            for k, v in data.items():
                if v is None:
                    if k in required:
                        resultado[k] = None
                    continue

                nueva_ruta = (
                    k
                    if ruta_actual == ""
                    else f"{ruta_actual}.{k}"
                )

                resultado[k] = cls.limpiar_none(
                    v,
                    requeridos,
                    nueva_ruta
                )

            return resultado

        elif isinstance(data, list):
           return [
                cls.limpiar_none(
                    item,
                    requeridos,
                    ruta_actual
                )
                for item in data
            ]

        return data


    @staticmethod
    def obtener_schema(documento):

        identificacion = documento.get("identificacion", {})
        tipo_dte = identificacion.get("tipoDte")

        if not tipo_dte:
            logger.info(
                "[SCHEMA_HELPER] No se detectó tipoDte. "
                "Usando contingencia-schema-v3."
            )
            return "contingencia-schema-v3"

        tipo_documento = (
            C002TipoDocumento.objects
            .filter(codigo=tipo_dte)
            .first()
        )

        if tipo_documento:
            logger.info(
                f"[SCHEMA_HELPER] tipoDte {tipo_dte} -> "
                f"{tipo_documento.schema_name}"
            )
            return tipo_documento.schema_name

        logger.error(
            f"[SCHEMA_HELPER] No existe C002TipoDocumento "
            f"para código {tipo_dte}"
        )

        return "desconocido"

    @classmethod
    def validar(cls, documento):
        # 1. Primero determinar el schema usando el documento interno
        schema_name = cls.obtener_schema(documento)

        logger.error(
            "[DEBUG_SCHEMA] tipo=%s schema=%s",
            documento["identificacion"]["tipoDte"],
            schema_name
        )

        # 2. Preparar una copia para validación MH
        documento_schema = cls.preparar_para_schema(
            documento,
            schema_name
        )        

        # 3. Leer campos requeridos del schema
        requeridos = cls.obtener_campos_requeridos(schema_name)

        # 4. Limpiar utilizando los required del schema
        documento_limpio = cls.limpiar_none(
            documento_schema,
            requeridos
        )

        logger.debug(
            "[SCHEMA_HELPER] Documento enviado a validar:\n%s",
            json.dumps(documento_limpio, indent=4, default=str)
        )

        # 5. Validar contra MH
        validador = validateSchema.schemaValidate({
            "tipo": schema_name,
            "json": documento_limpio
        })

        return validador.validar_schema()


    @staticmethod
    def obtener_campos_requeridos(schema_name):
        ruta = (
            Path(__file__).resolve()
            .parent.parent.parent
            / "schemas"
            / f"{schema_name}.json"
        )
        if not ruta.exists():
            raise FileNotFoundError(
                f"No existe el schema: {ruta}"
            )

        with ruta.open(encoding="utf-8") as f:
            schema = json.load(f)

        requeridos = {}

        def recorrer(nodo, ruta_actual=""):
            if not isinstance(nodo, dict):
                return

            required = nodo.get("required", [])

            if required:
                requeridos[ruta_actual] = set(required)

            # Objetos
            for nombre, valor in nodo.get("properties", {}).items():

                nueva_ruta = (
                    nombre
                    if ruta_actual == ""
                    else f"{ruta_actual}.{nombre}"
                )

                recorrer(valor, nueva_ruta)

            # Arrays de objetos
            if "items" in nodo:
                recorrer(
                    nodo["items"],
                    ruta_actual
                )

        recorrer(schema)

        logger.debug(
            "[SCHEMA_HELPER] Campos requeridos encontrados:\n%s",
            json.dumps(
                {
                    k: list(v)
                    for k, v in requeridos.items()
                },
                indent=4
            )
        )

        return requeridos


    @staticmethod
    def preparar_para_schema(documento, schema_name):
        """
        Elimina campos utilizados internamente por el sistema
        que no forman parte del JSON final esperado por MH.
        """
        documento = documento.copy()
        identificacion = documento.get("identificacion")

        if not identificacion:
            return documento

        identificacion = identificacion.copy()

        identificacion = documento.get("identificacion")
        if identificacion:
            identificacion = identificacion.copy()

            if schema_name == "fe-eret-v1":
                identificacion.pop("tipoDte", None)
                identificacion.pop("numeroControl", None)

            documento["identificacion"] = identificacion

        # Campos no permitidos para Evento de Retorno
        if schema_name == "fe-eret-v1":
            documento.pop("otrosDocumentos", None)

            resumen = documento.get("resumen")
            if resumen:
                resumen = resumen.copy()
                resumen.pop("observaciones", None)
                documento["resumen"] = resumen

        return documento    