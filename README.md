# Gestão de Solicitações — Associação Comunitária do Bairro Rio Branco

Aplicação web responsiva para registrar, organizar e acompanhar solicitações recebidas pela Associação Comunitária do Bairro Rio Branco. O projeto implementa o MVP definido no planejamento: autenticação, cadastro, consulta, filtros, prioridade, atribuição de responsável, atualização de situação e histórico de alterações.

## Histórico de evolução do projeto

O MVP da Associação Comunitária do Bairro Rio Branco foi desenvolvido
em etapas, com versionamento das alterações por meio do Git e publicação
no GitHub.

As entregas contemplam:

- Estrutura inicial da aplicação.
- Preparação para publicação e versionamento.
- Ajustes nos testes automatizados das solicitações.
- Configuração dos arquivos estáticos.
- Melhorias na visualização dos detalhes e do histórico das solicitações.

O projeto utiliza Django e tem como objetivo apoiar o registro,
acompanhamento e organização das demandas apresentadas pelos moradores.

## 1. Tecnologias e arquitetura

- Python 3.12
- Django 5.2 LTS
- SQLite (banco inicial do MVP)
- Bootstrap 5.3 + CSS próprio responsivo
- Django ORM, Forms, autenticação e proteção CSRF
- Arquitetura monolítica organizada em camadas. O Django utiliza o padrão MVT (Model–View–Template), com separação equivalente de responsabilidades entre dados/regras, tratamento das requisições e apresentação.

## 2. Funcionalidades implementadas

- Login por e-mail e senha e logout; endereços de e-mail devem ser únicos. Acesso às telas internas somente por usuário autenticado.
- Cadastro de solicitação com nome, contato, descrição, categoria, prioridade e responsável.
- Identificador único, data automática e situação inicial **Aberta**.
- Consulta com busca textual, filtros por categoria e situação e paginação de 20 registros.
- Detalhe da solicitação, atribuição/alteração de responsável e atualização de situação: Aberta, Em andamento, Aguardando ou Concluída.
- Histórico imutável pela interface comum, com usuário, data/hora e transição de situação.
- Painel com totais de solicitações abertas, em andamento, aguardando e concluídas.
- Categorias iniciais cadastradas por migração.
- Senhas armazenadas com PBKDF2-HMAC-SHA256, por meio do mecanismo nativo do Django; limite de cinco tentativas inválidas por e-mail/IP em uma janela de 15 minutos, sem armazenar o endereço IP em texto claro.

## 3. Requisitos

- Python 3.12 instalado.
- Git instalado (para versionamento).
- Acesso à internet no navegador para carregar Bootstrap e Bootstrap Icons via CDN. O backend funciona localmente sem depender de serviços externos.

## 4. Instalação local — Windows PowerShell

```powershell
# 1. Entre na pasta do projeto
cd rio-branco-mvp

# 2. Crie e ative o ambiente virtual
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instale as dependências
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Crie o arquivo de configuração local
Copy-Item .env.example .env
```

Edite `.env` e defina uma `SECRET_KEY` própria. Para gerar uma chave:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie o resultado para `SECRET_KEY` no `.env`. Em desenvolvimento, mantenha `DEBUG=True` e `ALLOWED_HOSTS=127.0.0.1,localhost`.

```powershell
# 5. Crie as tabelas e categorias iniciais
python manage.py migrate

# 6. Crie o primeiro usuário administrador (interativo; não existe senha padrão)
python manage.py criar_usuario_demo

# 7. Inicie o servidor
python manage.py runserver
```

Acesse http://127.0.0.1:8000/ e entre com o usuário e senha criados. Para administrar categorias e usuários, acesse `/admin/` com o usuário administrador.

## 5. Criar usuários colaboradores

No painel `/admin/`, crie um usuário em **Usuários**. O perfil de colaborador é criado automaticamente. Para permitir que ele entre, mantenha `Ativo` marcado. O campo de responsável no cadastro lista usuários ativos. O primeiro usuário criado pelo comando recebe perfil Administrador e acesso ao Django Admin. Os e-mails das contas precisam ser únicos; o formulário de administração impede duplicidades.

## 6. Testes

```powershell
python manage.py check
python manage.py test
```

Os testes automatizados verificam autenticação, cadastro com situação inicial Aberta, listagem protegida e gravação do histórico de atualização de situação.

## 7. Publicar no GitHub

Crie um repositório vazio no GitHub. Na pasta do projeto:

```powershell
git init
git add .
git commit -m "feat: MVP de gestão de solicitações comunitárias"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git push -u origin main
```

Não envie `.env`, banco SQLite, senhas ou dados reais de moradores. O `.gitignore` já exclui `.env` e arquivos `*.sqlite3`.

## 8. Implantação em servidor

O projeto inclui Gunicorn e WhiteNoise para servir arquivos estáticos. Em produção:

1. Configure `DEBUG=False`, `SECRET_KEY` forte, `ALLOWED_HOSTS` com o domínio e `CSRF_TRUSTED_ORIGINS` com a origem HTTPS.
2. Configure `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True` e `CSRF_COOKIE_SECURE=True` após habilitar HTTPS no domínio.
3. Use armazenamento persistente para o arquivo SQLite e mantenha cópias de segurança protegidas e testadas.
4. Execute `python manage.py migrate` e `python manage.py collectstatic --noinput`.
5. Inicie com `gunicorn config.wsgi:application`.

Exemplo de comando de inicialização (o provedor deve executar a partir da raiz do repositório):

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

**Limite conhecido do SQLite:** adequado ao MVP com volume e concorrência pequenos. O arquivo deve estar em disco persistente. Se houver múltiplos processos gravando simultaneamente, aumento relevante de usuários ou bloqueios de escrita, planeje migração para PostgreSQL. O uso do Django ORM facilita essa evolução, mas a migração e os testes precisam ser executados antes da troca.

## 9. Privacidade e segurança operacional

- Colete somente dados necessários ao retorno (nome, contato e descrição); não há campo para CPF.
- Use contas individuais; não compartilhe credenciais.
- Mantenha dependências atualizadas, HTTPS e backups protegidos.
- Não use dados reais em demonstrações ou testes sem autorização e finalidade definida.
- O MVP não inclui integração com WhatsApp/SMS, aplicativo nativo, consulta pública por moradores ou funcionamento offline.

## 10. Estrutura do projeto

```text
rio-branco-mvp/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── .gitignore
├── LICENSE
├── .github/
│   └── workflows/
├── config/
├── solicitacoes/
│   ├── management/
│   ├── migrations/
│   └── tests.py
├── templates/
├── static/
├── docs/
│   └── prototipos/
└── tests/
    ├── __init__.py
    └── README.md
```

**Observação sobre os testes:** os testes automatizados específicos da aplicação Django ficam em `solicitacoes/tests.py`, onde o Django os descobre pelo comando `python manage.py test`. A pasta raiz `tests/` está preparada para testes gerais e de integração do projeto.

## 11. Escopo e próximos incrementos

Este repositório entrega o MVP administrativo descrito no projeto. Não implementa integração automática com canais externos, notificações, relatórios avançados, portal público de moradores ou aplicativo móvel. Antes de uso real, faça avaliação com os usuários da associação, teste acessibilidade (contraste, teclado, zoom e leitores de tela), teste de carga compatível com o volume esperado e revisão das configurações do servidor.
