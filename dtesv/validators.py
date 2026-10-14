from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import string

class CustomUppercaseValidator:
    def __init__(self, min_uppercase_chars=1, min_numeric_chars=1, min_special_chars=1):
        self.min_uppercase_chars = min_uppercase_chars
        self.min_numeric_chars = min_numeric_chars
        self.min_special_chars = min_special_chars

    def validate(self, password, user=None):
        if sum(c.isupper() for c in password) < self.min_uppercase_chars:
            raise ValidationError(
                _("La contraseña debe contener al menos %(min_uppercase_chars)d mayúscula."),
                code='password_no_upper',
                params={'min_uppercase_chars': self.min_uppercase_chars},
            )

        if sum(c.isdigit() for c in password) < self.min_numeric_chars:
            raise ValidationError(
                _("La contraseña debe contener al menos %(min_numeric_chars)d número."),
                code='password_no_numeric',
                params={'min_numeric_chars': self.min_numeric_chars},
            )

        if sum(c in string.punctuation for c in password) < self.min_special_chars:
            raise ValidationError(
                _("La contraseña debe contener al menos %(min_special_chars)d carácter especial."),
                code='password_no_special',
                params={'min_special_chars': self.min_special_chars},
            )

    def get_help_text(self):
        return _(
            "La contraseña debe contener al menos %(min_uppercase_chars)d mayúscula, %(min_numeric_chars)d número y %(min_special_chars)d carácter especial."
        ) % {'min_uppercase_chars': self.min_uppercase_chars, 'min_numeric_chars': self.min_numeric_chars, 'min_special_chars': self.min_special_chars}