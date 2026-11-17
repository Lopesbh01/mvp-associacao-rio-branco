import hashlib
import hmac
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from .models import TentativaLogin

class EmailBackend(ModelBackend):
    """Autentica por e-mail e limita tentativas repetidas por e-mail/IP."""
    MAX_TENTATIVAS = 5
    JANELA_MINUTOS = 15

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = (kwargs.get('email') or username or '').strip().lower()
        if not email or not password:
            return None
        ip = (request.META.get('REMOTE_ADDR', 'unknown') if request else 'unknown')
        digest = hmac.new(settings.SECRET_KEY.encode(), ip.encode(), hashlib.sha256).hexdigest()
        limite = timezone.now() - timedelta(minutes=self.JANELA_MINUTOS)
        tentativas = TentativaLogin.objects.filter(
            email_normalizado=email, ip_digest=digest, sucesso=False, tentativa_em__gte=limite
        ).count()
        if tentativas >= self.MAX_TENTATIVAS:
            return None
        UserModel = get_user_model()
        matches = UserModel._default_manager.filter(email__iexact=email, is_active=True)
        user = matches.first() if matches.count() == 1 else None
        autenticado = bool(user and user.check_password(password) and self.user_can_authenticate(user))
        TentativaLogin.objects.create(email_normalizado=email[:254], ip_digest=digest, sucesso=autenticado)
        return user if autenticado else None
