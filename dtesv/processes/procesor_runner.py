# procesor_runner.py

from dtesv.processes.procesorDocMh import MainProcessor
from dtesv.models import Parametros , Company

def run_processor( codigoGen):
    # Obtén los parámetros necesarios

    parametros = Parametros.objects.get(company_id=Company.objects.get(id=1))

    # Crea y ejecuta el procesador principal
    main_processor = MainProcessor(codigoGen)
    return main_processor.run()
