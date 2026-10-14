from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import exceptions
from django.utils import timezone
from datetime import timedelta

TOKEN_EXPIRATION = timedelta(minutes=5)  # Configura la expiración deseada

class ExpiringTokenAuthentication(TokenAuthentication):
    def expires_in(self, token):
        time_elapsed = timezone.now() - token.created
        return time_elapsed < TOKEN_EXPIRATION

    def authenticate(self, request):
        auth = super().authenticate(request)

        if auth is None:
            return None

        user, token = auth

        if not self.expires_in(token):
            raise exceptions.AuthenticationFailed('Token expired')

        return user, token
