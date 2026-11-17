# Documento de Requisitos

# Laje do Modesto Reservas

## Versão

1.1

---

# Objetivo

O sistema Laje do Modesto Reservas tem como objetivo permitir que qualquer pessoa realize a reserva do espaço de eventos de maneira totalmente online, enquanto o administrador possui controle completo sobre reservas, pagamentos e disponibilidade do espaço.

---

# Público-alvo

## Cliente

Qualquer pessoa poderá acessar o sistema e realizar uma reserva, **sem precisar criar conta**.

A consulta pública de uma reserva (somente leitura) é feita com:

* CPF
* Código da reserva

Para **cancelar ou alterar** uma reserva, o cliente precisa ter uma conta (Área do Cliente):

* Cadastro com nome, e-mail, CPF e telefone.
* O e-mail é confirmado por um link enviado ao cliente; a senha é criada só depois dessa confirmação.
* Login com e-mail e senha.
* Recuperação de senha por e-mail.

Reservas feitas antes da criação da conta aparecem na Área do Cliente quando o e-mail confirmado for o mesmo da reserva.

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
* Consultar sua reserva (CPF e código).
* Criar conta, entrar e recuperar a senha.
* Ver todas as suas reservas na Área do Cliente.
* Atualizar nome e telefone.
* Cancelar uma reserva confirmada.
* Solicitar alteração de data e horário.

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

O início da festa deve ser em hora cheia, entre **08:00 e 21:00**. A duração base é de **8 horas**, com possibilidade de horas extras enquanto o término não passar das 05:00.

# Cancelamentos

Somente o cliente logado pode cancelar, e apenas reservas confirmadas e de data futura.

* Até 7 dias antes do evento: o cancelamento é feito na hora, sem taxa.
* Com menos de 7 dias: é cobrada taxa de 20% do valor total; o pedido fica aguardando a aprovação do administrador.

Antes de confirmar, o sistema mostra ao cliente a taxa e o valor a devolver.

---

# Alterações

Somente o cliente logado pode pedir alteração, e apenas de reservas confirmadas e de data futura.

A alteração dependerá da aprovação do administrador. A duração contratada é mantida, e o horário original continua bloqueado até a decisão.

---

# Responsividade

O sistema será desenvolvido com foco principal em dispositivos móveis (Mobile First).

Também será totalmente funcional em computadores.

---

# Segurança

O painel administrativo será protegido por autenticação utilizando Token.

Somente o administrador poderá acessar funções administrativas.

A Área do Cliente também usa Token, mas as permissões são separadas: o token de um cliente não acessa funções administrativas, e o do administrador não acessa a Área do Cliente.

Cada cliente só enxerga e altera as próprias reservas. Tentativas de login, cadastro e recuperação de senha têm limite por hora, e as respostas não revelam se um e-mail está cadastrado.

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

**Versão:** 1.1

**Status:** Em desenvolvimento