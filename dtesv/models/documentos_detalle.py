from django.db import models


class DocumentosDetalle(models.Model):

        numItem = models.IntegerField(db_column='numItem') 
        tipoItem = models.CharField(max_length=2,db_column='tipoItem',blank=True, null=True)
        cantidad = models.DecimalField(max_digits=18,db_column='cantidad', decimal_places=6, blank=True, null=True)
        codigo = models.CharField(max_length=25,db_column='codigo',blank=True, null=True)
        codTributo = models.ForeignKey('C015Tributos', models.DO_NOTHING, db_column='codTributo', blank=True, null=True,related_name = 'documento_detalle_codTributo' )  # Field name made lowercase. 
        uniMedida= models.IntegerField(db_column='uniMedida',blank=False, null=False) 
        descripcion = models.CharField(max_length=188,db_column='descripcion',blank=False, null=False)
        precioUni =  models.DecimalField(max_digits=18,db_column='precioUni', decimal_places=6, blank=False, null=False)
        montoDescu =  models.DecimalField(max_digits=18,db_column='montoDescu', decimal_places=6, blank=False, null=False)
        ventaNoSuj =  models.DecimalField(max_digits=18,db_column='ventaNoSuj', decimal_places=6, blank=False, null=False)
        ventaExenta =  models.DecimalField(max_digits=18,db_column='ventaExenta', decimal_places=6, blank=False, null=False)
        ventaGravada = models.DecimalField(max_digits=18,db_column='ventaGravada', decimal_places=6, blank=False, null=False)
        noGravado= models.DecimalField(max_digits=18,db_column='noGravado', decimal_places=6, blank=False, null=False)
        ivaItem = models.DecimalField(max_digits=18,db_column='ivaItem', decimal_places=6, blank=False, null=False)        
        codigoGeneracion_id = models.ForeignKey('Documentos', models.DO_NOTHING, db_column='codigoGeneracion_id', blank=True, null=True,related_name = 'documento_detalle_codigoGeneracion_id' )  # Field name made lowercase. 
        psv = models.DecimalField(max_digits=18,db_column='psv', decimal_places=6, default = 0.0, blank=False, null=False)            
        numeroDocumento =models.CharField(max_length=36,db_column='numeroDocumento',blank=True, null=True)
        codigoRetencionMH = models.ForeignKey('C006RetencionIva', models.DO_NOTHING, db_column='codigoRetencionMH', blank=True, null=True,related_name = 'documento_detalle_codigoRetencionMH' )  # Field name made lowercase. 
        tipoDte = models.ForeignKey('C002TipoDocumento', models.DO_NOTHING, db_column='tipoDte', blank=True, null=True,related_name = 'documento_detalle_tipoDte' )  # Field name made lowercase. 
        tipoDoc = models.ForeignKey('C007TipoGeneraciondoc', models.DO_NOTHING, db_column='tipoDoc', blank=True, null=True,related_name = 'documento_detalle_tipoDoc' )  # Field name made lowercase. 
        fechaEmision = models.DateField(blank=True, null=True ,db_column='fechaEmision')
        

        class Meta:
            managed = True
            db_table = 'DOCUMENTOS_DETALLE'
            unique_together = (('numItem', 'codigoGeneracion_id'),)
