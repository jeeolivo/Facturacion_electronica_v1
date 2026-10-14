
from __future__ import absolute_import, unicode_literals
from celery import Celery 
import os
from celery.signals import setup_logging
import logging
from decouple import config
from kombu import Exchange, Queue
#from dotenv import load_dotenv



# establecer el entorno para que Django conozca la configuración
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Facturacion_electronica.settings')

# crea una instancia de la aplicación Celery y configúrala utilizando la configuración de Django
app = Celery('dtesv')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    CELERYD_CONCURRENCY=15  # Define el número de workers (por ejemplo, 10 workers)
)

broker_connection_retry_on_startup = True


redis_host = config('REDIS_HOST', default='localhost')  # Coloca la dirección IP de tu servidor Redis
redis_port = config('REDIS_PORT', default=6379, cast=int)  # Coloca el puerto en el que Redis está escuchando
app.conf.broker_url = f'redis://{redis_host}:{redis_port}/'
app.conf.result_backend = f'redis://{redis_host}:{redis_port}/1'
#app.conf.task_default_queue = 'general_tasks'

app.conf.task_queues = (
    Queue('urgent', Exchange('urgent'), routing_key='urgent'),
    Queue('default', Exchange('default'), routing_key='default'),
)
   
app.conf.task_routes = {
    # Asignar las tareas a las colas correspondientes
    'procesar_documentos': {'queue': 'urgent', 'routing_key': 'urgent'},
    'send_emails_for_pending_documents': {'queue': 'default', 'routing_key': 'default'},
}  
 
# Prioridad por defecto para las tareas
app.conf.task_default_priority = 5
app.conf.task_acks_late = True  # Aceptación tardía de tareas para reintentos

# carga tareas desde todas las aplicaciones de Django que tienen un archivo tasks.py
app.autodiscover_tasks()

@setup_logging.connect
def configure_logging(**kwargs):
    logging.basicConfig(filename='celery.log', level=logging.INFO)

