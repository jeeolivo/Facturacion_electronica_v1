from django.db import models
from .documentos import Documentos


class DocumentosLote(models.Model):


    version = models.IntegerField(db_column='version', blank=True, null=True)
    ambiente= models.ForeignKey('C001AmbienteDestino', models.DO_NOTHING, db_column='ambienteTrabajo', blank=True, null=True,related_name = 'documentosLote_ambiente_trabajo')
    versionApp=models.IntegerField(db_column='versionApp', blank=True, null=True)
    estado= models.CharField(max_length=50,db_column='estado',blank=True, null=True)
    idEnvio=  models.CharField(primary_key=True,max_length=36,db_column='idEnvio')
    codigoLote= models.CharField(max_length=36 ,db_column='codigoLote',blank=True, null=True)
    fhProcesamiento= models.DateTimeField(db_column='fhProcesamiento',blank=True, null=True)
    clasificaMsg=  models.IntegerField(db_column='clasificaMsg', blank=True, null=True)
    codigoMsg= models.CharField(max_length=10,db_column='codigoMsg',blank=True, null=True)
    descripcionMsg= models.TextField(db_column='descripcionMsg',blank=True, null=True) 
    detalledocumentoslote = models.ManyToManyField(Documentos, related_name='detalledocumentoslote', blank=True)
    observaciones= models.TextField(db_column='observaciones',blank=True, null=True) 

    class Meta:
        managed = True
        db_table = 'DOCUMENTOS_LOTE'
    objects = models.Manager()
       
    def crear_documentos_lote(self,idEnvio, version, ambiente, version_app, estado, codigo_lote, fh_procesamiento, clasifica_msg, codigo_msg, descripcion_msg, documentos_relacionados):
        # Crea un nuevo objeto DocumentosLote
        documentos_lote = DocumentosLote(
            idEnvio = idEnvio,
            version=version,
            ambiente=ambiente,
            versionApp=version_app,
            estado=estado,
            codigoLote=codigo_lote,
            fhProcesamiento=fh_procesamiento,
            clasificaMsg=clasifica_msg,
            codigoMsg=codigo_msg,
            descripcionMsg=descripcion_msg
        )

        # Guarda el objeto DocumentosLote en la base de datos
        documentos_lote.save()

        # Asocia los documentos relacionados al DocumentosLote
        for documento in documentos_relacionados:
            documentos_lote.detalledocumentoslote.add(documento)

        return documentos_lote