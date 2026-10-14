from django.db import models


class CAT023TipodeDocumentoenContingencia(models.Model):
    codigo = models.CharField(db_column='CODIGO', primary_key=True, max_length=3)  # Field name made lowercase.
    valor = models.CharField(db_column='VALOR', max_length=50, blank=True, null=True)  # Field name made lowercase.
    schema_name = models.CharField(max_length=100, blank=True, null=True)
    version_work = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'C002_TIPO_DOCUMENTO_CONTINGENCIA'

    def __str__(self):
        return self.valor