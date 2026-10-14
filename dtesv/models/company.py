from django.db import models
from django.conf import settings
from .user import User
import os
from django.utils.deconstruct import deconstructible

from django.core.files.storage import FileSystemStorage
 

#current_directory = os.path.dirname(os.path.abspath(__file__))
#directorio_actual = os.getcwd()
#mymodule_dir = os.path.join( directorio_actual, 'Facturacion_electronica\\dtesv' )
#logos_dir = os.path.join( mymodule_dir, 'company_logos' )

fs = FileSystemStorage(location='/opt/DTESV/dtesv/Facturacion_electronica/dtesv/company_logos/')


class Company(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name='companies_company', blank=True)
    emisor = models.OneToOneField('dtesv.Emisor', on_delete=models.CASCADE, blank=True, null=True) 
    logo = models.ImageField(storage=fs)
    

    def __str__(self):
        return self.name