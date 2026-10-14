# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class C013Municipio(models.Model):
    id = models.AutoField(primary_key=True )
    codigo = models.CharField(db_column='CODIGO',  max_length=2)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=125)  # Field name made lowercase.
    cod_departamento = models.ForeignKey('C012Departamento', models.DO_NOTHING, blank=True, null=True,db_column='COD_DEPARTAMENTO',related_name = 'municipio_departamento')  # Field name made lowercase.
    ## 2024-09-19: Este campo se agrega para control a requemiento de MH modificacion de catalogos, para Sistema de Facturación v1.1
    distr_munic = models.CharField(blank=True, null=True, db_column='COD_DISTRMUNI', max_length=2)  # Updated field type
   
    class Meta:
        managed = True
        db_table = 'C013_MUNICIPIO'
        unique_together = (('codigo', 'cod_departamento'),)

    def __str__(self):
        return self.nombre