from django.db import models
from django.conf import settings


class Emisor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    nit = models.CharField(max_length=14)
    dui = models.CharField(max_length=14)
    nrc = models.CharField(max_length=8)
    nombre = models.CharField(max_length=250)
    codactividad = models.ForeignKey('C019ActividadEconomica', models.DO_NOTHING, db_column='codActividad',related_name ='emisor_codActividad')    
    nombrecomercial = models.CharField(db_column='nombreComercial', max_length=150, blank=True, null=True)
    tipoestablecimiento = models.ForeignKey('C009TipoEstablecimiento', models.DO_NOTHING, db_column='tipoEstablecimiento')
    departamento = models.ForeignKey('C012Departamento', models.DO_NOTHING, db_column='departamento', blank=True, null=True ,related_name ='emisor_departamento')
    municipio = models.ForeignKey('C013Municipio', models.DO_NOTHING, db_column='municipio', blank=True, null=True,related_name ='emisor_municipio')
    direccion_complemento = models.CharField(max_length=200)
    telefono = models.CharField(max_length=30)
    codestablemh = models.CharField(db_column='codEstableMH', max_length=4, blank=True, null=True)
    codestable = models.CharField(db_column='codEstable', max_length=4, blank=True, null=True)
    codpuntoventamh = models.CharField(db_column='codPuntoVentaMH', max_length=4, blank=True, null=True)
    codpuntoventa = models.CharField(db_column='codPuntoVenta', max_length=4, blank=True, null=True)
    correo = models.CharField(max_length=100)
    categoria = models.CharField(max_length=125, blank=True, null=True)
    whatsapp = models.CharField(max_length=30, blank=True, null=True)
    activo = models.IntegerField(blank=True, null=True)
    passwordpri = models.TextField(db_column='passwordPri', blank=True, null=True)
    mh_auth = models.CharField(max_length=175, blank=True, null=True)
    ambiente_trabajo = models.ForeignKey('C001AmbienteDestino', models.DO_NOTHING, db_column='ambiente', blank=True, null=True,related_name = 'ambiente_trabajo' )
    tipoItemExpor =models.ForeignKey('C011TipoItem', models.DO_NOTHING, db_column='tipoItemExpor',blank=True, null=True ,related_name ='emisor_tipoItemExpor')    
    recintoFiscal =models.ForeignKey('C027RecintoFiscal', models.DO_NOTHING, db_column='recintoFiscal',blank=True, null=True ,related_name ='emisor_recintoFiscal')
    regimen =models.ForeignKey('C028Regimen', models.DO_NOTHING, db_column='regimen',blank=True, null=True ,related_name ='emisor_regimen')     
    encontingencia = models.IntegerField(blank=False,null=False,default=0)
    tipocontingencia = models.IntegerField(blank=True,null=True)
    ###  2024-09-19: Se realiza cambios a la tabla se agrega la nueva columna para requemiento de MH modificacion de catalogos, para Sistema de Facturación v1.1
    munidistrito = models.ForeignKey('C014Distritos', models.DO_NOTHING, db_column='munidistrito', blank=True, null=True,related_name = 'emisor_munidistrito')

    class Meta:
        managed = True
        db_table = 'EMISOR'
    
    def __str__(self):
        return self.nombre
