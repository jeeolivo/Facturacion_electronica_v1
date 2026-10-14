from django.db import models


class DocumentosAsociados(models.Model):
    codigoGeneracion = models.CharField(primary_key=True,max_length=36,db_column='codigoGeneracion')
    codigoGeneracion_asoc =models.ForeignKey('Documentos', models.DO_NOTHING, db_column='codigoGeneracion_asoc', related_name = 'documento_asociado_codigoGeneracion_asoc' )  # Field name made lowercase.     
    id_emisor = models.ForeignKey('Emisor', models.DO_NOTHING, db_column='id_emisor')

    class Meta:
        managed = True
        db_table = 'DOCUMENTOS_ASOCIADOS'
        unique_together = (('codigoGeneracion', 'codigoGeneracion_asoc'),)
