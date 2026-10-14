# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ExtencionEntrega(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(db_column='Nombre', max_length=125, blank=True, null=True)  # Field name made lowercase.
    placa_vehiculo = models.CharField(max_length=10, blank=True, null=True)
    docuentrega = models.CharField(db_column='docuEntrega', max_length=20, blank=True, null=True)  # Field name made lowercase.
    id_emisor = models.ForeignKey('Emisor', models.DO_NOTHING, db_column='id_emisor')

    class Meta:
        managed = True
        db_table = 'EXTENCION_ENTREGA'
        unique_together = (('codigo', 'id_emisor'),)
