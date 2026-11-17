# Testes do projeto

Os testes automatizados do fluxo de solicitações estão em
`solicitacoes/tests.py`, junto à aplicação Django que eles verificam.
Essa organização permite que o comando `python manage.py test` os descubra
automaticamente.

Esta pasta fica reservada para testes de integração ou de componentes
gerais do projeto que não pertençam exclusivamente à aplicação
`solicitacoes`.
