# Banco de Dados

# Laje do Modesto Reservas

## Objetivo

Este documento descreve a estrutura do banco de dados utilizada pelo sistema **Laje do Modesto Reservas**.

O banco de dados é responsável por armazenar todas as informações do sistema de forma organizada, segura e consistente.

---

# Banco utilizado

## Desenvolvimento

SQLite

## Produção

PostgreSQL

---

# Entidades do Sistema

Atualmente o sistema é composto pelas seguintes entidades:

* Clientes
* Reservas
* Status das Reservas
* Cupons
* Adicionais
* Pagamentos
* Usuário Administrador

---

# Cliente

Responsável por armazenar os dados do cliente.

Principais informações:

* Nome
* CPF
* Telefone
* E-mail

Cada cliente poderá possuir várias reservas.

---

# Reserva

É a entidade principal do sistema.

Cada reserva possui:

* Cliente
* Código da reserva
* Data
* Hora de início
* Hora de término
* Quantidade de convidados
* Valor total
* Status
* Forma de pagamento

Também poderá possuir:

* Cupons
* Adicionais

---

# Status da Reserva

Os status controlam a situação da reserva.

Exemplos:

* PENDENTE
* CONFIRMADA
* CANCELADA
* ALTERACAO_SOLICITADA
* CANCELAMENTO_SOLICITADO

---

# Pagamentos

Responsável por registrar:

* Valor
* Forma de pagamento
* Data
* Situação do pagamento

Exemplos de situação:

* Pendente
* Pago
* Cancelado

---

# Cupons

Cada cupom poderá possuir:

* Código
* Percentual de desconto
* Data de validade
* Ativo ou inativo

---

# Adicionais

Itens opcionais da reserva.

Exemplos:

* Churrasqueira
* Freezer
* Decoração
* Outros serviços

---

# Usuário Administrador

O sistema possuirá apenas um usuário administrador.

Esse usuário será responsável por toda a administração do sistema.

---

# Relacionamentos

Um cliente pode possuir várias reservas.

Uma reserva pertence a um único cliente.

Uma reserva possui apenas um status.

Uma reserva poderá possuir vários adicionais.

Uma reserva poderá utilizar um cupom.

Uma reserva possuirá um pagamento.

---

# Objetivo

A estrutura do banco foi planejada para facilitar futuras expansões do sistema sem necessidade de alterações significativas.

---

**Versão:** 1.0

**Status:** Em desenvolvimento
