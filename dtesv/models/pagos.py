from django.db import models


class Pagos(models.Model):

    numRec = models.CharField(db_column='numRec',primary_key=True, max_length=12)
    codigogeneracion_doc =  models.ForeignKey('Documentos', models.DO_NOTHING, db_column='codigoGeneracion_doc', blank=True, null=True,related_name = 'pagos_codigoGeneracion_doc' )  # Field name made lowercase. 
    codigo_forma_pago = models.CharField(db_column='codigo_forma_pago', max_length=20, blank=True, null=True)  # Field name made lowercase.
    monto = models.DecimalField(max_digits=18,db_column='monto', decimal_places=6, blank=False, null=False)
    plazo = models.CharField(db_column='plazo', max_length=12)
    periodo = models.CharField(db_column='periodo', max_length=12)
    


    class Meta:
            managed = True
            db_table = 'PAGOS'
            unique_together = (('numRec', 'codigogeneracion_doc'),)
