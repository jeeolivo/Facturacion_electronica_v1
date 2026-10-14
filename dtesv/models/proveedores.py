from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils import timezone


class Proveedor(models.Model):

    
    codigo = models.CharField(primary_key=True, max_length=55)
    empresa = models.ForeignKey('Emisor', models.DO_NOTHING,related_name = 'proveedor_empresa')
    tipodocumento = models.ForeignKey('C022TipoDocumentoIdentificacionReceptor', models.DO_NOTHING, db_column='tipodocumento', blank=True, null=True,related_name = 'proveedor_tipo_documento_identific' )  # Field name made lowercase.
    numdocumento = models.CharField(db_column='numDocumento', max_length=18)  # Field name made lowercase.
    nrc = models.CharField(max_length=10, blank=True, null=True)
    nombre = models.CharField(max_length=255)    
    codactividad = models.ForeignKey('C019ActividadEconomica', models.DO_NOTHING, db_column='codActividad',related_name = 'proveedor_codActividad')
    nombrecomercial = models.CharField(db_column='nombreComercial', max_length=255)  # Field name made lowercase.
    telefono = models.CharField(max_length=50, blank=True, null=False)
    correo = models.CharField(max_length=100, blank=True, null=False)
    complemento = models.TextField(blank=True, null=True)
    municipio = models.ForeignKey('C013Municipio', models.DO_NOTHING, db_column='municipio',related_name = 'proveedor_municipio')
    departamento = models.ForeignKey('C012Departamento', models.DO_NOTHING, db_column='departamento',related_name = 'proveedor_departamento')
    codpais = models.ForeignKey('C020Pais', models.DO_NOTHING, db_column='codPais', blank=True, null=True,related_name = 'proveedor_codpais')  # Field name made lowercase.
    tipopersona = models.ForeignKey('C029TipoPersona', models.DO_NOTHING, db_column='tipoPersona', blank=True, null=True,related_name = 'proveedor_tipopersona')  # Field name made lowercase.
    tiporeceptor = models.CharField(db_column='tipoReceptor', max_length=10, blank=True, null=True)  # Field name made lowercase.
    # agrego este campo para manejar sucursales de  los clientes 
    codigoPadre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    ###  2024-09-19: Se realiza cambios a la tabla se agrega la nueva columna para requemiento de MH modificacion de catalogos, para Sistema de Facturación v1.1
    munidistrito = models.ForeignKey('C014Distritos', models.DO_NOTHING, db_column='munidistrito', blank=True, null=True,related_name = 'proveedor_munidistrito')  


    class Meta: 
        managed = True
        db_table = 'PROVEEDOR'
        unique_together = (('codigo', 'empresa'),) ##'tiporeceptor'),)

    def __str__(self):
        return self.nombre
