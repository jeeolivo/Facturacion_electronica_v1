from django.db import models


class Documentos(models.Model):

    tipodocumento = models.ForeignKey('C002TipoDocumento', models.DO_NOTHING, db_column='tipo_documento', blank=True, null=True,related_name = 'documento_tipo_documento' )  # Field name made lowercase. 
    clase_documento = models.CharField(max_length=2,db_column='clase_documento')
    num_documento =models.CharField(max_length=50,db_column='Num_documento')
    fecEmi = models.DateField(blank=True, null=True ,db_column='fecEmi')
    totalNoSuj = models.DecimalField(max_digits=18 ,db_column='totalNoSuj', decimal_places=6, blank=True, null=True)
    totalExenta  = models.DecimalField(max_digits=18 ,db_column='totalExenta', decimal_places=6, blank=True, null=True)
    horEmi = models.TimeField(db_column='horEmi',blank=True, null=True)
    descuGravada = models.DecimalField(max_digits=18,db_column='descuGravada', decimal_places=6, blank=True, null=True)
    porcentajeDescuento= models.DecimalField(max_digits=18,db_column='porcentajeDescuento', decimal_places=6, blank=True, null=True)
    totalDescu= models.DecimalField(max_digits=18 ,db_column='totalDescu', decimal_places=6, blank=True, null=True)
    iva =models.DecimalField(max_digits=18 ,db_column='iva', decimal_places=6, blank=True, null=True)
    ivaRete1 = models.DecimalField(max_digits=18,db_column='ivaRete1', decimal_places=6, blank=True, null=True)
    ivaPerci1 = models.DecimalField(max_digits=18, db_column='ivaPerci1',decimal_places=6, blank=True, null=True)
    reteRenta = models.DecimalField(max_digits=18, db_column='reteRenta',decimal_places=6, blank=True, null=True)
    totalGravada  = models.DecimalField(max_digits=18, db_column='totalGravada',decimal_places=6, blank=True, null=True)
    subTotalVentas = models.DecimalField(max_digits=18, db_column='subTotalVentas',decimal_places=6, blank=True, null=True)
    descuNoSuj = models.DecimalField(max_digits=18, db_column='descuNoSuj',decimal_places=6, blank=True, null=True)
    descuExenta = models.DecimalField(max_digits=18, db_column='descuExenta',decimal_places=6, blank=True, null=True)
    totalNoGravado = models.DecimalField(max_digits=18, db_column='totalNoGravado',decimal_places=6, blank=True, null=True)
    saldoFavor =  models.DecimalField(max_digits=18, db_column='saldoFavor',decimal_places=6, blank=True, null=True)
    totalPagar =  models.DecimalField(max_digits=18, db_column='totalPagar',decimal_places=6, blank=True, null=True)
    montoTotalOperacion =  models.DecimalField(max_digits=18, db_column='montoTotalOperacion',decimal_places=6, blank=True, null=True)
    condicionOperacion = models.ForeignKey('C016CondicionOperacion', models.DO_NOTHING, db_column='condicionOperacion', blank=True, null=True,related_name = 'documento_condicionOperacion' )  # Field name made lowercase. 
    codigo_iva =  models.ForeignKey('C015Tributos', models.DO_NOTHING, db_column='codigo_iva', blank=True, null=True,related_name = 'documento_codigo_iva' )  # Field name made lowercase. 
    totalLetras = models.CharField(max_length=255,db_column='totalLetras')
    receptor_id = models.ForeignKey('Receptor', models.DO_NOTHING, db_column='receptor_id', blank=True, null=True,related_name = 'documento_receptor_id' )  # Field name made lowercase. 
    pagos = models.IntegerField(db_column='pagos', blank=True, null=True)
    numPagoElectronico = models.CharField(max_length=50,db_column='numPagoElectronico',blank=True, null=True)
    vendedor_id = models.CharField(max_length=10,db_column='vendedor_id',blank=True, null=True)
    estado = models.CharField(max_length=10,db_column='estado',blank=True, null=True) 
    numeroControl =models.CharField(max_length=255,db_column='numeroControl',blank=True, null=True)
    codigoGeneracion = models.CharField(primary_key=True,max_length=36,db_column='codigoGeneracion')
    tipoModelo =models.ForeignKey('C003ModeloFacturacion', models.DO_NOTHING, db_column='tipoModelo', blank=True, null=True,related_name = 'documento_tipoModelo' )
    tipoOperacion = models.ForeignKey('C007TipoGeneraciondoc', models.DO_NOTHING, db_column='tipoOperacion', blank=True, null=True,related_name = 'documento_tipoOperacion' )
    tipoTransmision = models.ForeignKey('C004TipoTransmision', models.DO_NOTHING, db_column='tipoTransmision', blank=True, null=True,related_name = 'documento_tipoTransmision' )
    tipoContingencia = models.ForeignKey('C005TipoContingencia', models.DO_NOTHING, db_column='tipoContingencia', blank=True, null=True,related_name = 'documento_tipoContingencia' )
    motivoContin = models.CharField(max_length=255,db_column='motivoContin',blank=True, null=True) 
    tipoMoneda = models.CharField(max_length=10,db_column='tipoMoneda',blank=True, null=True) 
    emisor_id = models.ForeignKey('Emisor', models.DO_NOTHING, db_column='emisor_id', blank=True, null=True,related_name = 'documento_emisor_id' )
    cod_entrega = models.CharField(max_length=10,db_column='cod_entrega',blank=True, null=True) 
    observaciones_entrega= models.CharField(max_length=255,db_column='observaciones_entrega',blank=True, null=True) 
    bienTitulo = models.ForeignKey('C025BienesRemitidosTitulos', models.DO_NOTHING, db_column='bienTitulo', blank=True, null=True,related_name = 'documento_bienTitulo' )
    numeroDocumento_rel_guid =  models.CharField(max_length=36,db_column='numeroDocumento_rel_guid',blank=True, null=True)
    numeroDocumento_rel_corr =  models.CharField(max_length=55,db_column='numeroDocumento_rel_corr',blank=True, null=True) 
    recintoFiscal = models.ForeignKey('C027RecintoFiscal', models.DO_NOTHING, db_column='recintoFiscal', blank=True, null=True,related_name = 'documento_recintoFiscal' )
    regimen =models.ForeignKey('C028Regimen', models.DO_NOTHING, db_column='regimen', blank=True, null=True,related_name = 'documento_regimen' )
    tipoItemExpor = models.IntegerField(db_column='tipoItemExpor', blank=True, null=True)
    seguro = models.DecimalField(max_digits=18, db_column='seguro',decimal_places=6, blank=True, null=True)
    flete = models.DecimalField(max_digits=18, db_column='flete',decimal_places=6, blank=True, null=True)
    codIncoterms = models.ForeignKey('C031Incoterms', models.DO_NOTHING, db_column='codIncoterms', blank=True, null=True,related_name = 'documento_codIncoterms' )
    selloRecibido = models.CharField(max_length=50,db_column='selloRecibido',blank=True, null=True) 
    observaciones_mh = models.TextField(db_column='observaciones_mh',blank=True, null=True) 
    fecha_proceso_mh =models.DateTimeField(db_column='fecha_proceso_mh',blank=True, null=True)
    cod_sucursal = models.CharField(max_length=8,db_column='cod_sucursal',blank=True, null=True) 
    observacion_proceso =models.TextField(db_column='observacion_proceso',blank=True, null=True) 
    detalle = models.ForeignKey('DocumentosDetalle', on_delete=models.CASCADE, related_name='documento_detalles', blank=True, null=True)
    estado_anulado =models.TextField(db_column='estado_anulado',blank=True, null=True) 
    selloInvalidacion = models.CharField(max_length=50,db_column='selloInvalidacion',blank=True, null=True) 
    fecha_anula_mh =models.DateTimeField(db_column='fecha_anula_mh',blank=True, null=True)
    en_contingencia = models.BooleanField(db_column='en_contingencia',default=False)
    enviado_movil = models.BooleanField(db_column='enviado_movil',default=False)
    codigoLotelocal = models.CharField(max_length=36 ,db_column='codigoGeneracionLote',blank=True, null=True)
    codigoLotemh = models.CharField(max_length=36 ,db_column='codigo_lote_mh',blank=True, null=True)
    email_enviado = models.BooleanField(db_column='email_enviado',default=False)
    totalSujetoRetenido = models.DecimalField(max_digits=18, db_column='totalSujetoRetenido',decimal_places=6, blank=True, null=True)
    totalIVAretenido = models.DecimalField(max_digits=18, db_column='totalIVAretenido',decimal_places=6, blank=True, null=True)
      # agrego este campo para namejar sucursales de  los clientes 
    receptor_origen = models.ForeignKey('Receptor', models.DO_NOTHING, db_column='receptor_origen', blank=True, null=True,related_name = 'documento_receptor_origen_id' )  # Field name made lowercase. 
    # este campo lo usare para realizar o trabajar la reimpresion masiva de representaciones graficas
    rutaEntrega = models.CharField(max_length=6,db_column='rutaEntrega',blank=True, null=True) 
    # estes es para guardar el numero de order de Compra 
    orden_compra =  models.CharField(max_length=120,db_column='orden_compra',blank=True, null=True) 
    # este es el movitivo por invalidacion
    motivoInvalidacion = models.CharField(max_length=255,db_column='motivoInvalidacion',blank=True, null=True) 
    # guradare los Cofigosde GEneracion de las Invalidaciones 
    codigoGenInvalida = models.CharField(max_length=36,db_column='codigoGenInvalida' ,blank=True, null=True)

    # guradare los Cofigosde GEneracion de las Invalidaciones 
    anuladoErp = models.BooleanField(db_column='anuladoErp',default=False)
    # Esto permitira ingresar el nuevo campo para los receptores tipo proveedor
    proveedor_id = models.ForeignKey('Proveedor', models.DO_NOTHING, db_column='proveedor_id', blank=True, null=True,related_name = 'documento_proveedor_id' )  # Field name made lowercase.  


    @classmethod
    def actualizar_registro(cls, codigo_generacion, nuevo_estado):
        documento = cls.objects.get(codigoGeneracion=codigo_generacion)
        documento.estado = nuevo_estado
        documento.save()




    class Meta:
        managed = True
        db_table = 'DOCUMENTOS'
        unique_together = (('codigoGeneracion','tipodocumento', 'emisor_id'),)
