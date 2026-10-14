from django.utils import timezone
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.sessions.models import Session

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Verificar si la cookie de sesión está presente
        if not request.COOKIES.get('sessionid') and request.user.is_authenticated:
            logout(request)
            messages.info(request, 'Has sido desconectado automáticamente por inactividad.')  # Mensaje de desconexión

        return response
 
    
class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lógica para rastrear usuarios activos
        if request.user.is_authenticated:
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
        
        response = self.get_response(request)
        return response        