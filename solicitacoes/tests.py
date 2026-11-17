from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Categoria, Historico, Solicitacao

User = get_user_model()

class FluxoSolicitacaoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='colaborador', email='colaborador@example.org', password='SenhaSegura-12345')
        self.categoria = Categoria.objects.create(nome='Iluminação pública')


    def test_login_aceita_email_e_senha(self):
        response = self.client.post(reverse('login'), {
            'username': 'colaborador@example.org',
            'password': 'SenhaSegura-12345',
        })
        self.assertRedirects(response, reverse('inicio'))

    def test_bloqueia_apos_cinco_tentativas_invalidas_na_janela(self):
        for _ in range(5):
            self.client.post(reverse('login'), {
                'username': 'colaborador@example.org', 'password': 'senha-incorreta',
            })
        response = self.client.post(reverse('login'), {
            'username': 'colaborador@example.org', 'password': 'SenhaSegura-12345',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_telas_internas_exigem_login(self):
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_cadastro_define_status_aberta_e_cria_historico(self):
        self.client.login(username='colaborador@example.org', password='SenhaSegura-12345')
        response = self.client.post(reverse('nova_solicitacao'), {
            'nome_solicitante': 'Carlos Mendes',
            'contato_solicitante': '(31) 99999-0000',
            'descricao': 'Lâmpada apagada na praça do bairro.',
            'categoria': self.categoria.pk,
            'prioridade': 'alta',
            'responsavel': self.user.pk,
        })
        self.assertRedirects(response, reverse('consultar_solicitacoes'))
        solicitacao = Solicitacao.objects.get()
        self.assertEqual(solicitacao.status, Solicitacao.Status.ABERTA)
        self.assertEqual(solicitacao.usuario_registro, self.user)
        self.assertTrue(Historico.objects.filter(solicitacao=solicitacao, status_novo='aberta').exists())

    def test_atualizacao_de_status_registra_transicao(self):
        solicitacao = Solicitacao.objects.create(
            nome_solicitante='Maria', contato_solicitante='31999999999', descricao='Reparo na calçada',
            categoria=self.categoria, prioridade='media', usuario_registro=self.user,
        )
        self.client.login(username='colaborador@example.org', password='SenhaSegura-12345')
        response = self.client.post(reverse('atualizar_status', args=[solicitacao.pk]), {
            'status': 'em_andamento', 'observacao': 'Equipe acionada.'
        })
        self.assertRedirects(response, reverse('detalhe_solicitacao', args=[solicitacao.pk]))
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, 'em_andamento')
        log = Historico.objects.get(solicitacao=solicitacao, status_novo='em_andamento')
        self.assertEqual(log.status_anterior, 'aberta')
        self.assertEqual(log.usuario, self.user)

    def test_listagem_protegida(self):
        self.client.login(username='colaborador@example.org', password='SenhaSegura-12345')
        response = self.client.get(reverse('consultar_solicitacoes'))
        self.assertEqual(response.status_code, 200)
