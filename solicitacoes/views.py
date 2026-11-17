from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import SolicitacaoForm, AtualizarStatusForm, FiltroSolicitacaoForm, AtribuirResponsavelForm
from .models import Categoria, Historico, Solicitacao

@login_required
def inicio(request):
    total = Solicitacao.objects.count()
    counts = {key: Solicitacao.objects.filter(status=key).count() for key, _ in Solicitacao.Status.choices}
    recentes = Solicitacao.objects.select_related('categoria', 'responsavel').all()[:5]
    return render(request, 'solicitacoes/inicio.html', {
        'total': total, 'abertas': counts[Solicitacao.Status.ABERTA],
        'andamento': counts[Solicitacao.Status.EM_ANDAMENTO],
        'aguardando': counts[Solicitacao.Status.AGUARDANDO],
        'concluidas': counts[Solicitacao.Status.CONCLUIDA], 'recentes': recentes,
    })

@login_required
def nova_solicitacao(request):
    if request.method == 'POST':
        form = SolicitacaoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                solicitacao = form.save(commit=False)
                solicitacao.usuario_registro = request.user
                solicitacao.status = Solicitacao.Status.ABERTA
                solicitacao.save()
                Historico.objects.create(solicitacao=solicitacao, usuario=request.user, acao='Solicitação cadastrada', status_novo=Solicitacao.Status.ABERTA)
                if solicitacao.responsavel_id:
                    Historico.objects.create(solicitacao=solicitacao, usuario=request.user, acao=f'Responsável atribuído: {solicitacao.responsavel.get_full_name() or solicitacao.responsavel.username}')
            messages.success(request, f'Solicitação #{solicitacao.pk} cadastrada com sucesso!')
            return redirect('consultar_solicitacoes')
        messages.error(request, 'Verifique os campos destacados e corrija as informações.')
    else:
        form = SolicitacaoForm()
    return render(request, 'solicitacoes/formulario.html', {'form': form, 'titulo': 'Nova solicitação'})

@login_required
def consultar_solicitacoes(request):
    form = FiltroSolicitacaoForm(request.GET or None)
    qs = Solicitacao.objects.select_related('categoria', 'responsavel', 'usuario_registro').all()
    if form.is_valid():
        q = form.cleaned_data.get('q', '').strip()
        status = form.cleaned_data.get('status')
        categoria = form.cleaned_data.get('categoria')
        if q:
            query = Q(descricao__icontains=q) | Q(nome_solicitante__icontains=q) | Q(contato_solicitante__icontains=q)
            if q.isdigit():
                query |= Q(pk=int(q))
            qs = qs.filter(query)
        if status:
            qs = qs.filter(status=status)
        if categoria:
            qs = qs.filter(categoria=categoria)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'solicitacoes/lista.html', {'form': form, 'page_obj': page, 'total_filtrado': paginator.count, 'total_geral': Solicitacao.objects.count(), 'abertas': Solicitacao.objects.filter(status=Solicitacao.Status.ABERTA).count(), 'andamento': Solicitacao.objects.filter(status=Solicitacao.Status.EM_ANDAMENTO).count(), 'concluidas': Solicitacao.objects.filter(status=Solicitacao.Status.CONCLUIDA).count()})

@login_required
def detalhe_solicitacao(request, pk):
    solicitacao = get_object_or_404(Solicitacao.objects.select_related('categoria', 'responsavel', 'usuario_registro'), pk=pk)
    historicos = solicitacao.historicos.select_related('usuario').all()
    return render(request, 'solicitacoes/detalhe.html', {'solicitacao': solicitacao, 'historicos': historicos, 'status_form': AtualizarStatusForm(instance=solicitacao), 'responsavel_form': AtribuirResponsavelForm(instance=solicitacao)})

@login_required
def atualizar_status(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk)
    if request.method != 'POST':
        return redirect('detalhe_solicitacao', pk=pk)
    form = AtualizarStatusForm(request.POST, instance=solicitacao)
    if form.is_valid():
        novo_status = form.cleaned_data['status']
        observacao = form.cleaned_data.get('observacao', '').strip()
        anterior = solicitacao.status
        if novo_status == anterior:
            messages.info(request, 'A solicitação já possui essa situação.')
        else:
            with transaction.atomic():
                solicitacao = Solicitacao.objects.select_for_update().get(pk=pk)
                anterior = solicitacao.status
                solicitacao.status = novo_status
                solicitacao.save(update_fields=['status'])
                Historico.objects.create(solicitacao=solicitacao, usuario=request.user, acao='Situação atualizada', status_anterior=anterior, status_novo=novo_status, observacao=observacao)
            messages.success(request, 'Situação atualizada e registrada no histórico.')
    else:
        messages.error(request, 'Não foi possível atualizar a situação. Verifique os dados informados.')
    return redirect('detalhe_solicitacao', pk=pk)


@login_required
def atualizar_responsavel(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk)
    if request.method != 'POST':
        return redirect('detalhe_solicitacao', pk=pk)
    form = AtribuirResponsavelForm(request.POST, instance=solicitacao)
    if form.is_valid():
        novo_responsavel = form.cleaned_data.get('responsavel')
        anterior_id = solicitacao.responsavel_id
        novo_id = novo_responsavel.pk if novo_responsavel else None
        if anterior_id == novo_id:
            messages.info(request, 'A solicitação já está atribuída a esse responsável.')
        else:
            with transaction.atomic():
                solicitacao = Solicitacao.objects.select_for_update().get(pk=pk)
                solicitacao.responsavel = novo_responsavel
                solicitacao.save(update_fields=['responsavel'])
                nome = (novo_responsavel.get_full_name() or novo_responsavel.username) if novo_responsavel else 'A definir'
                Historico.objects.create(solicitacao=solicitacao, usuario=request.user, acao=f'Responsável atualizado: {nome}')
            messages.success(request, 'Responsável atualizado e registrado no histórico.')
    else:
        messages.error(request, 'Não foi possível atualizar o responsável. Verifique os dados informados.')
    return redirect('detalhe_solicitacao', pk=pk)
