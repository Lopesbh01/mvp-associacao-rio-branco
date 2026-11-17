from django.conf import settings
from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField('nome', max_length=80, unique=True)
    descricao = models.CharField('descrição', max_length=255, blank=True)
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.nome

class Solicitacao(models.Model):
    class Prioridade(models.TextChoices):
        BAIXA = 'baixa', 'Baixa'
        MEDIA = 'media', 'Média'
        ALTA = 'alta', 'Alta'

    class Status(models.TextChoices):
        ABERTA = 'aberta', 'Aberta'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        AGUARDANDO = 'aguardando', 'Aguardando'
        CONCLUIDA = 'concluida', 'Concluída'

    nome_solicitante = models.CharField('nome do solicitante', max_length=120)
    contato_solicitante = models.CharField('contato', max_length=80)
    descricao = models.TextField('descrição', max_length=500)
    data_registro = models.DateTimeField('data de registro', default=timezone.now, editable=False)
    prioridade = models.CharField('prioridade', max_length=10, choices=Prioridade.choices, default=Prioridade.MEDIA)
    status = models.CharField('situação', max_length=20, choices=Status.choices, default=Status.ABERTA)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='solicitacoes', verbose_name='categoria')
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitacoes_responsavel', verbose_name='responsável')
    usuario_registro = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='solicitacoes_registradas', verbose_name='registrado por')

    class Meta:
        ordering = ['-data_registro', '-id']
        verbose_name = 'solicitação'
        verbose_name_plural = 'solicitações'
        indexes = [models.Index(fields=['status', 'data_registro']), models.Index(fields=['categoria', 'status'])]

    def __str__(self):
        return f'Solicitação #{self.pk} — {self.nome_solicitante}'

class Historico(models.Model):
    solicitacao = models.ForeignKey(Solicitacao, on_delete=models.PROTECT, related_name='historicos', verbose_name='solicitação')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='historicos', verbose_name='usuário')
    data_alteracao = models.DateTimeField('data da alteração', auto_now_add=True)
    acao = models.CharField('ação', max_length=120)
    status_anterior = models.CharField('situação anterior', max_length=20, blank=True)
    status_novo = models.CharField('nova situação', max_length=20, blank=True)
    observacao = models.TextField('observação', blank=True)

    class Meta:
        ordering = ['-data_alteracao', '-id']
        verbose_name = 'registro de histórico'
        verbose_name_plural = 'históricos'

    def __str__(self):
        return f'{self.acao} — solicitação #{self.solicitacao_id}'

class PerfilUsuario(models.Model):
    class Tipo(models.TextChoices):
        ADMINISTRADOR = 'administrador', 'Administrador'
        COLABORADOR = 'colaborador', 'Colaborador'

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_associacao')
    tipo = models.CharField('perfil', max_length=20, choices=Tipo.choices, default=Tipo.COLABORADOR)

    class Meta:
        verbose_name = 'perfil de usuário'
        verbose_name_plural = 'perfis de usuários'

    def __str__(self):
        return f'{self.usuario.username} — {self.get_tipo_display()}'


class TentativaLogin(models.Model):
    email_normalizado = models.CharField(max_length=254)
    ip_digest = models.CharField(max_length=64)
    tentativa_em = models.DateTimeField(auto_now_add=True)
    sucesso = models.BooleanField(default=False)

    class Meta:
        ordering = ['-tentativa_em']
        indexes = [models.Index(fields=['email_normalizado', 'ip_digest', 'tentativa_em'])]
        verbose_name = 'tentativa de autenticação'
        verbose_name_plural = 'tentativas de autenticação'
