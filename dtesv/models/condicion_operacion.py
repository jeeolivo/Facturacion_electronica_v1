
from django.db import models


class C016CondicionOperacion(models.Model):
    codigo = models.IntegerField(db_column='CODIGO', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'C016_CONDICION_OPERACION'
