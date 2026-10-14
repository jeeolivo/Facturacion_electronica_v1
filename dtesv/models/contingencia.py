from django.db import models
from .documentos import Documentos

class contingencias(models.Model):
     # Campos de Identificacion
    version = models.IntegerField()
    ambiente = models.ForeignKey('C001AmbienteDestino', models.DO_NOTHING, db_column='ambiente', blank=True, null=True,related_name = 'contingencia_ambiente' )
    codigoGeneracion = models.CharField(max_length=36, unique=True)
    fTransmision = models.DateField()
    hTransmision = models.TimeField()
    
    # Campos de Emisor (Relación uno a uno)
    emisor= models.ForeignKey('Emisor', models.DO_NOTHING, db_column='emisor', blank=True, null=True,related_name = 'contingencia_emisor_id' )
    
    # Campos de DetalleDTE (Relación muchos a muchos)
    detalleDTE = models.ManyToManyField(Documentos, related_name='Documentos_contingencia', blank=True)
    
    # Campos de Motivo (Relación uno a uno)
    fInicio = models.DateField()
    fFin = models.DateField()
    hInicio = models.TimeField()
    hFin = models.TimeField()
    tipoContingencia = models.ForeignKey('C005TipoContingencia', models.DO_NOTHING, db_column='tipoContingencia', blank=True, null=True,related_name = 'contingencia_tipo' )
    motivoContingencia = models.CharField(max_length=500, null=True)
    selloRecepcion =models.CharField(max_length=45,null=True,blank=True)
    estado = models.CharField(max_length=10,db_column='estado',blank=True, null=True)
    observacion_proceso = models.TextField(db_column='observaciones_proceso',blank=True, null=True) 
    observaciones_mh = models.TextField(db_column='observaciones_mh',blank=True, null=True) 
   

    class Meta:
        managed = True
        db_table = 'CONTINGENCIA'
       
