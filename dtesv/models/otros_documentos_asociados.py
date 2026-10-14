# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class OtrosDocumentosAsociados(models.Model):
    numero_doc = models.CharField(max_length=50)
    guid_doc_asoc = models.CharField(max_length=36, blank=True, null=True)
    num_doc_asoc = models.CharField(max_length=50)
    fecha_documento = models.DateField(blank=True, null=True)
    other_tipo_documento_asoc = models.CharField(max_length=3)
    coddocasociado = models.IntegerField(db_column='codDocAsociado', blank=True, null=True)  # Field name made lowercase.
    tipo_documento_oasoc = models.CharField(max_length=3)
    emisor_id = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'OTROS_DOCUMENTOS_ASOCIADOS'
