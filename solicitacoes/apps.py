from django.apps import AppConfig

class SolicitacoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solicitacoes'
    verbose_name = 'Gestão de solicitações'

    def ready(self):
        import solicitacoes.signals  # noqa: F401
