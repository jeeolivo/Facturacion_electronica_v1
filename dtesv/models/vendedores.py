from django.db import models


class Vendedores(models.Model):
    codigo = models.CharField(db_column='codigo',max_length=16,primary_key=True)
    nombre =   models.CharField(max_length=50, blank=True, null=True)
    area =  models.CharField(max_length=249, blank=True, null=True)
    activo = models.BooleanField(db_column='activo',default=False)
    tipo = models.CharField(max_length=16, blank=True, null=True)
    sucursal = models.CharField(max_length=16, blank=True, null=True)
    telefono = models.CharField(max_length=100, blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'vendedores'

    def __str__(self):
        return self.codigo+":"+self.nombre