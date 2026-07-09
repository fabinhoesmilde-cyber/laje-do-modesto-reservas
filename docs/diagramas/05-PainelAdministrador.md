# 05 - Painel do Administrador

## Objetivo

Este documento descreve o funcionamento do Painel Administrativo do sistema **Laje do Modesto Reservas**.

O painel administrativo é destinado exclusivamente ao proprietário da Laje do Modesto, permitindo o gerenciamento completo das reservas e das operações do sistema.

---

# Acesso

O acesso ao painel será realizado através de autenticação utilizando usuário e senha.

Após a autenticação, o sistema fornecerá um Token de acesso, que será utilizado para autorizar todas as operações administrativas.

Somente o administrador poderá acessar este painel.

---

# Funcionalidades

O administrador poderá:

* Realizar login.
* Encerrar sessão (Logout).
* Visualizar o Dashboard.
* Pesquisar reservas.
* Visualizar todas as reservas.
* Aprovar alterações de reservas.
* Rejeitar alterações de reservas.
* Aprovar cancelamentos.
* Rejeitar cancelamentos.
* Criar reservas manualmente.
* Editar reservas.
* Bloquear datas.
* Gerenciar cupons de desconto.
* Gerenciar adicionais.
* Visualizar pagamentos.
* Gerar relatórios.

---

# Dashboard

O painel exibirá informações resumidas para facilitar o acompanhamento do negócio.

Exemplos de indicadores:

* Total de reservas.
* Reservas confirmadas.
* Alterações pendentes.
* Cancelamentos pendentes.
* Reservas do dia.
* Datas bloqueadas.

---

# Pesquisa de Reservas

O administrador poderá localizar reservas utilizando:

* Código da reserva.
* Nome do cliente.
* CPF.
* Data da reserva.
* Status da reserva.

---

# Gestão de Reservas

O administrador poderá visualizar todas as informações da reserva, incluindo:

* Nome do cliente.
* CPF.
* Código da reserva.
* Data.
* Horário de início.
* Horário de término.
* Quantidade de convidados.
* Valor da reserva.
* Forma de pagamento.
* Status da reserva.

---

# Aprovação de Alterações

Quando um cliente solicitar alteração da reserva, o administrador poderá:

* Aprovar a alteração.
* Rejeitar a alteração.

Após a decisão, o sistema atualizará automaticamente o status da reserva.

---

# Aprovação de Cancelamentos

Quando um cliente solicitar o cancelamento, o administrador poderá:

* Aprovar o cancelamento.
* Rejeitar o cancelamento.

O sistema aplicará automaticamente as regras de negócio referentes à política de cancelamento.

---

# Segurança

Todas as funcionalidades administrativas estarão protegidas por autenticação via Token.

Caso o Token seja inválido ou expire, o acesso será bloqueado e o administrador deverá realizar um novo login.

---

# Objetivo Futuro

O Painel Administrativo continuará evoluindo com novas funcionalidades, como:

* Dashboard financeiro.
* Calendário administrativo.
* Relatórios avançados.
* Gestão de pagamentos.
* Controle de datas bloqueadas.
* Exportação de relatórios em PDF.

---

**Versão:** 1.0

**Status:** Em desenvolvimento
