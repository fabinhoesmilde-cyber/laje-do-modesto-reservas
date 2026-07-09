# Documento de Requisitos

# Laje do Modesto Reservas

## Versão

1.0

---

# Objetivo

O sistema Laje do Modesto Reservas tem como objetivo permitir que qualquer pessoa realize a reserva do espaço de eventos de maneira totalmente online, enquanto o administrador possui controle completo sobre reservas, pagamentos e disponibilidade do espaço.

---

# Público-alvo

## Cliente

Qualquer pessoa poderá acessar o sistema e realizar uma reserva.

Não será necessário criar uma conta.

A consulta da reserva será realizada utilizando:

* CPF
* Código da reserva

---

## Administrador

O sistema possuirá apenas um administrador.

O administrador será o proprietário da Laje do Modesto.

Não existirão níveis de acesso ou outros usuários administrativos.

---

# Funcionalidades do Cliente

O cliente poderá:

* Visualizar informações sobre o espaço.
* Consultar datas disponíveis.
* Realizar reservas.
* Escolher adicionais.
* Utilizar cupons de desconto.
* Efetuar pagamento.
* Consultar sua reserva.
* Solicitar alteração.
* Solicitar cancelamento.

---

# Funcionalidades do Administrador

O administrador poderá:

* Realizar login.
* Encerrar sessão.
* Visualizar dashboard.
* Pesquisar reservas.
* Aprovar alterações.
* Rejeitar alterações.
* Aprovar cancelamentos.
* Rejeitar cancelamentos.
* Criar reservas manualmente.
* Editar reservas.
* Bloquear datas.
* Gerenciar cupons.
* Gerenciar adicionais.
* Visualizar pagamentos.
* Gerar relatórios.

---

# Pagamentos

O sistema aceitará:

* PIX
* Cartão de Crédito

A reserva somente será confirmada após a confirmação do pagamento integral.

Não haverá pagamento parcial.

---

# Horários

Internamente o sistema trabalhará utilizando:

* Data
* Hora de início
* Hora de término

Na interface do cliente poderão existir opções como:

* Manhã
* Tarde
* Noite

Essas opções apenas facilitarão o preenchimento dos horários.

---
# Regra de Encerramento dos Eventos

Toda locação deverá terminar no máximo até **05:00 da manhã**.

Caso um evento comece no período da noite, por exemplo às **23:00**, o horário máximo de encerramento será **05:00 da manhã do dia seguinte**, mesmo que isso resulte em menos horas de evento.

Essa regra existe porque o espaço precisa estar liberado pela manhã para limpeza, organização e preparação para possíveis novas reservas no mesmo dia.

O sistema deverá impedir reservas que ultrapassem esse limite de horário.

# Cancelamentos

O cliente poderá solicitar cancelamento.

O cancelamento dependerá da aprovação do administrador.

---

# Alterações

O cliente poderá solicitar alteração da reserva.

A alteração dependerá da aprovação do administrador.

---

# Responsividade

O sistema será desenvolvido com foco principal em dispositivos móveis (Mobile First).

Também será totalmente funcional em computadores.

---

# Segurança

O painel administrativo será protegido por autenticação utilizando Token.

Somente o administrador poderá acessar funções administrativas.

---

# Banco de Dados

Desenvolvimento:

SQLite

Produção:

PostgreSQL

---

# Objetivo Final

Colocar o sistema em produção para utilização real pela Laje do Modesto, oferecendo uma plataforma moderna, segura e simples para clientes e administrador.

---

**Versão:** 1.0

**Status:** Em desenvolvimento
