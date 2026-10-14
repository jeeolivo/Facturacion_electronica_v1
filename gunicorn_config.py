# gunicorn_config.py
from pathlib import Path

base_path = Path(__file__).resolve(strict=True).parent

bind = "192.168.1.29:8000"  # La dirección y el puerto en los que escuchará Gunicorn
workers = 4            # Número de procesos de trabajadores, ajusta según tus necesidades
timeout = 120          # Tiempo máximo de respuesta de una solicitud
loglevel = "debug"      # Nivel de registro: debug, info, warning, error, critical
accesslog = "/opt/DTESV/dtesv/Facturacion_electronica/access.log"
errorlog = "/opt/DTESV/dtesv/Facturacion_electronica/error.log"
capture_output = True   # Capturar la salida (stdout y stderr) de los trabajadores

# Configuración de Gunicorn
worker_class = 'gevent'  # o usa cualquier clase que prefieras
static_path = base_path / 'Facturacion_electronica' / 'dtesv' / 'static'
static_url = '/static/'

# Configuración de archivos estáticos
if static_path.exists():
    static_path = str(static_path)
    static_url = static_url

