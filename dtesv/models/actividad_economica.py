from django.db import models


class C019ActividadEconomica(models.Model):
    codigo = models.CharField(db_column='CODIGO', primary_key=True, max_length=6)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=250)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'C019_ACTIVIDAD_ECONOMICA'

    def __str__(self):
        return self.nombre