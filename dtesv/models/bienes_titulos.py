
from django.db import models


class C025BienesRemitidosTitulos(models.Model):
    codigo = models.CharField(primary_key=True, max_length=2)
    descripcion = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'C025_BIENES_REMITIDOS_TITULOS'
