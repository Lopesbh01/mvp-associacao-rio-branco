from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('solicitacoes/nova/', views.nova_solicitacao, name='nova_solicitacao'),
    path('solicitacoes/', views.consultar_solicitacoes, name='consultar_solicitacoes'),
    path('solicitacoes/<int:pk>/', views.detalhe_solicitacao, name='detalhe_solicitacao'),
    path('solicitacoes/<int:pk>/situacao/', views.atualizar_status, name='atualizar_status'),
    path('solicitacoes/<int:pk>/responsavel/', views.atualizar_responsavel, name='atualizar_responsavel'),
]
