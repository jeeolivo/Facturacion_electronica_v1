### 2024-09-19: Este modelo se agrega de acuerdo a nuevo requemiento de MH modificacion de catalogos, para Sistema de Facturación v1.1
from django.db import models

class C014Distritos (models.Model):
    
    id = models.AutoField(primary_key=True )
    codigo = models.CharField(db_column='CODIGO',  max_length=2)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=125)  # Field name made lowercase.
    cod_departamento = models.ForeignKey('C012Departamento', models.DO_NOTHING, blank=True, null=True,db_column='COD_DEPARTAMENTO',related_name = 'distrito_departamento')  # Field name made lowercase.
    #cod_municipio = models.ForeignKey('C013Municipio', models.DO_NOTHING, blank=True, null=True, db_column='COD_DISTRMUNI', related_name='distrito_municipio')  # Relación con C013Municipio
    #cod_municipio = models.ManyToManyField('C013Municipio', related_name='distrito_municipio')

    class Meta:
        managed = True
        db_table = 'C014_DISTRITOS'
        unique_together = (('codigo', 'cod_departamento'),)

    def __str__(self):
        return self.nombre