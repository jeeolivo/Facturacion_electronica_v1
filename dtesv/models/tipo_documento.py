# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class C002TipoDocumento(models.Model):
    codigo = models.CharField(db_column='CODIGO', primary_key=True, max_length=3)  # Field name made lowercase.
    valor = models.CharField(db_column='VALOR', max_length=50, blank=True, null=True)  # Field name made lowercase.
    schema_name = models.CharField(max_length=100, blank=True, null=True)
    version_work = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'C002_TIPO_DOCUMENTO'

    def __str__(self):
        return self.valor