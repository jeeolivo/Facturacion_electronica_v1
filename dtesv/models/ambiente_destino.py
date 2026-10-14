
from django.db import models


class C001AmbienteDestino(models.Model):
    codigo = models.CharField(db_column='CODIGO', max_length=2)  # Field name made lowercase.
    valor = models.CharField(db_column='VALOR', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'C001_AMBIENTE_DESTINO'

    def __str__(self):
        return self.valor
