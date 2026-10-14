from django.contrib.auth.models import AbstractUser ,Group,Permission
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.utils import timezone




class User(AbstractUser):
    puede_procesar_contingencia = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)
    #puede_re_procesar = models.BooleanField(default=False)
   # companies = models.ManyToManyField('dtesv.Company', related_name='users_company')
    #companies = models.ForeignKey('dtesv.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='users_company')

    # def save(self, *args, **kwargs):
    #     # 2024-10-15: Mejora en acceso y registro de last_activity que servira para saber cantidad de usuarios en linea.
    #     if self.password:
    #         try:
    #             # Verifica si la contraseña está cambiando
    #             if not self.pk:
    #                 # Si el usuario es nuevo, encripta la contraseña
    #                # validate_password(self.password, self.user)
    #                 self.password = make_password(self.password)
    #             else:
    #                 # Si el usuario ya existe, compara la contraseña actual con la nueva
    #                 usuario_actual = User.objects.get(pk=self.pk)
    #                 #validate_password(self.password, usuario_actual.username)
    #                 ##if self.password != usuario_actual.password:
    #                 ##    print("OK")
    #                 if not check_password(self.password, usuario_actual.password):
    #                     self.password = make_password(self.password)
    #                    # self.password = make_password(self.password)
    #         except ValidationError as e:
    #             raise ValidationError({'password': ', '.join(e.messages)})
    #     super().save(*args, **kwargs)
    def __str__(self):
        return self.email
                    
            # CODIGO ORIGEN
            # # Verifica si la contraseña está cambiando
            # if not self.pk:
            #     # Si el usuario es nuevo, encripta la contraseña
            #     self.password = make_password(self.password)
            # else:
            #     # Si el usuario ya existe, compara la contraseña actual con la nueva
            #     usuario_actual = User.objects.get(pk=self.pk)
            #     if self.password != usuario_actual.password:
            #        # self.password = make_password(self.password)
            #         print('Contraseña Cambiada')

    

    
  