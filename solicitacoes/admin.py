from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import Categoria, Historico, PerfilUsuario, Solicitacao, TentativaLogin

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa')
    list_filter = ('ativa',)
    search_fields = ('nome',)

class HistoricoInline(admin.TabularInline):
    model = Historico
    extra = 0
    can_delete = False
    readonly_fields = ('usuario', 'data_alteracao', 'acao', 'status_anterior', 'status_novo', 'observacao')

@admin.register(Solicitacao)
class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_solicitante', 'categoria', 'prioridade', 'status', 'responsavel', 'data_registro')
    list_filter = ('status', 'prioridade', 'categoria')
    search_fields = ('nome_solicitante', 'contato_solicitante', 'descricao')
    readonly_fields = ('data_registro', 'usuario_registro')
    inlines = [HistoricoInline]

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo')
    list_filter = ('tipo',)


User = get_user_model()

class AssociacaoUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este e-mail já está associado a outra conta.')
        return email

class AssociacaoUserChangeForm(UserChangeForm):
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este e-mail já está associado a outra conta.')
        return email

admin.site.unregister(User)

@admin.register(User)
class AssociacaoUserAdmin(BaseUserAdmin):
    add_form = AssociacaoUserCreationForm
    form = AssociacaoUserChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(TentativaLogin)
class TentativaLoginAdmin(admin.ModelAdmin):
    list_display = ('email_normalizado', 'tentativa_em', 'sucesso')
    list_filter = ('sucesso', 'tentativa_em')
    search_fields = ('email_normalizado',)
    readonly_fields = ('email_normalizado', 'ip_digest', 'tentativa_em', 'sucesso')
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
