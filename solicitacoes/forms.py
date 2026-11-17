from django import forms
from django.contrib.auth import get_user_model
from .models import Categoria, Solicitacao

User = get_user_model()

class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ['nome_solicitante', 'contato_solicitante', 'descricao', 'categoria', 'prioridade', 'responsavel']
        widgets = {
            'nome_solicitante': forms.TextInput(attrs={'placeholder': 'Ex.: Maria da Silva', 'autocomplete': 'name'}),
            'contato_solicitante': forms.TextInput(attrs={'placeholder': '(31) 99999-9999', 'autocomplete': 'tel'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'maxlength': 500, 'placeholder': 'Descreva a necessidade apresentada pelo morador.'}),
            'categoria': forms.Select(),
            'prioridade': forms.Select(),
            'responsavel': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.filter(ativa=True)
        self.fields['categoria'].empty_label = 'Selecione uma categoria'
        self.fields['responsavel'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'username')
        self.fields['responsavel'].required = True
        self.fields['responsavel'].empty_label = 'Selecione um responsável'
        self.fields['prioridade'].choices = [('', 'Selecione a prioridade'), *Solicitacao.Prioridade.choices]
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_contato_solicitante(self):
        value = self.cleaned_data['contato_solicitante'].strip()
        if len(value) < 8:
            raise forms.ValidationError('Informe um contato válido para retorno.')
        return value

class AtualizarStatusForm(forms.ModelForm):
    observacao = forms.CharField(label='Observação (opcional)', required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Registre um detalhe relevante sobre a atualização.'}))
    class Meta:
        model = Solicitacao
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': 'form-select'})}

class FiltroSolicitacaoForm(forms.Form):
    q = forms.CharField(required=False, label='Buscar', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por ID, descrição ou solicitante'}))
    status = forms.ChoiceField(required=False, choices=[('', 'Todas as situações'), *Solicitacao.Status.choices], widget=forms.Select(attrs={'class': 'form-select'}))
    categoria = forms.ModelChoiceField(required=False, queryset=Categoria.objects.none(), empty_label='Todas as categorias', widget=forms.Select(attrs={'class': 'form-select'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.all()


class AtribuirResponsavelForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ['responsavel']
        widgets = {'responsavel': forms.Select(attrs={'class': 'form-select'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsavel'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'username')
        self.fields['responsavel'].required = False
        self.fields['responsavel'].empty_label = 'A definir'
