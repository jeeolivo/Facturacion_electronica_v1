from django.db import models
from django.conf import settings
from .user import User
import os
 

 

class Parametros(models.Model):
    name = models.CharField(max_length=255,default="Parametros")
    ambiente = models.ForeignKey('C001AmbienteDestino', models.DO_NOTHING, db_column='ambienteTrabajo', blank=True, null=True,related_name = 'settings_ambiente_trabajo')
    url_firmador = models.CharField(max_length=255)
    url_autentication = models.CharField(max_length=255)
    url_dte = models.CharField(max_length=255)
    url_dte_lote = models.CharField(max_length=255 ,  default="https://apitest.dtes.mh.gob.sv/fesv/recepcionlote/")
    url_dte_consulta = models.CharField(max_length=255 ,  default="https://api.dtes.mh.gob.sv/fesv/recepcion/consultadte/")
    url_dte_lote_consulta = models.CharField(max_length=255 ,  default="https://apitest.dtes.mh.gob.sv/fesv/recepcion/consultadtelote/")
    url_invalidacion = models.CharField(max_length=255 ,  default="https://apitest.dtes.mh.gob.sv/fesv/anulardte")    
    url_contingencia = models.CharField(max_length=255 ,  default="https://apitest.dtes.mh.gob.sv/fesv/contingencia")    
    url_email_api_login = models.CharField(max_length=255 , default="http://192.168.1.48:4000/api/login")
    user_login_email =  models.CharField(max_length=50, default="mi user")
    pass_login_email=  models.CharField(max_length=255, default="mi pass")
    url_email_api = models.CharField(max_length=255 , default="http://192.168.1.48:4000/api/correo")
    url_getconsectivoSF = models.CharField(max_length=255 , default="http://192.168.1.53:5010/api/consecutivos/")
    url_setconsectivoSF = models.CharField(max_length=255 , default="http://192.168.1.53:5010/api/consecutivosUp/")
    contigencia_defaul =models.ForeignKey('C005TipoContingencia', models.DO_NOTHING, db_column='contigencia_defaul', blank=True, null=True,related_name = 'settings_contingencia')
    interval_ejecute = models.IntegerField()
    company_id = models.ForeignKey('Company', models.DO_NOTHING, db_column='company_id',default=1, blank=False, null=False,related_name = 'parametros_company_id')
    automatizacion_activa =models.BooleanField(default=True)
    hora_inicio = models.IntegerField(default=9)
    hora_fin =  models.IntegerField(default=18)
    intervalo_tiempo =models.IntegerField(default=60000)
    attachment_email_path = models.CharField(max_length=255 , default="C:\\app\\")
    attachment_files_path = models.CharField(max_length=255 , default="C:\\app\\")
    noticias = models.CharField(max_length=255, blank=True)
    

    class Meta:
        managed = True
        db_table = 'settings'

    def __str__(self):
        return self.name