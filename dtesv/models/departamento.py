
from django.db import models


class C012Departamento(models.Model):
    codigo = models.CharField(db_column='CODIGO', primary_key=True, max_length=2)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=125, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'C012_DEPARTAMENTO'

    def __str__(self):
        return self.nombre