
from django.db import models


class C010CodtipoServicio(models.Model):
    codigo = models.CharField(db_column='CODIGO', primary_key=True, max_length=2)  # Field name made lowercase.
    valor = models.CharField(db_column='VALOR', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'C010_CODTIPO_SERVICIO'
