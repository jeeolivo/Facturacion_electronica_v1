from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from .models import User , Company ,Parametros ,Emisor ,Vendedores
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
# Register your models here.
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

    def clean_password(self):
        password = self.cleaned_data.get("password")
        user = self.instance

        try:
            validate_password(password,user.username)
        except ValidationError as e:
            raise ValidationError({'password': ', '.join(e.messages)})

        return password

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm

class CompanyAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)

admin.site.register(User,CustomUserAdmin)
admin.site.register(Company,CompanyAdmin)
admin.site.register(Parametros)
admin.site.register(Emisor)
admin.site.register(Vendedores)



admin.site.site_header = 'Panel de Administración DTESV'
