from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from solicitacoes.models import PerfilUsuario

class Command(BaseCommand):
    help = 'Cria um usuário inicial interativamente, sem senha padrão embutida.'
    def handle(self, *args, **options):
        User = get_user_model()
        username = input('Usuário (login): ').strip()
        email = input('E-mail: ').strip()
        first_name = input('Nome: ').strip()
        if not username or not email:
            raise CommandError('Usuário e e-mail são obrigatórios.')
        if User.objects.filter(username=username).exists():
            raise CommandError('Esse usuário já existe.')
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError('Esse e-mail já está associado a outra conta.')
        password = __import__('getpass').getpass('Senha (mínimo 12 caracteres): ')
        if len(password) < 12:
            raise CommandError('A senha deve ter pelo menos 12 caracteres.')
        user = User.objects.create_user(username=username, email=email, first_name=first_name, password=password)
        PerfilUsuario.objects.update_or_create(usuario=user, defaults={'tipo': PerfilUsuario.Tipo.ADMINISTRADOR})
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['is_staff', 'is_superuser'])
        self.stdout.write(self.style.SUCCESS(f'Usuário administrativo {username} criado.'))
