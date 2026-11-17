# Regras de Negócio

# Laje do Modesto Reservas

## Objetivo

Este documento descreve todas as regras de negócio que deverão ser respeitadas pelo sistema Laje do Modesto Reservas.

As regras aqui definidas representam o funcionamento real da empresa e deverão ser consideradas durante o desenvolvimento de todas as funcionalidades.

---

# RN-100 — Regras de Reserva

## RN-101 — Horário máximo do evento

Toda locação deverá terminar obrigatoriamente até às **05:00 da manhã**.

O sistema deverá impedir reservas que ultrapassem esse horário.

**Motivo:**

Garantir tempo suficiente para limpeza e preparação da Laje para um novo evento.

---

## RN-102 — Permanência após o evento

Após o término da reserva, os clientes deverão deixar o espaço.

Não será permitida permanência após o horário contratado.

---

## RN-103 — Entrada antecipada

O cliente poderá entrar antes do horário oficial da reserva para organizar a festa.

Essa entrada antecipada somente será permitida quando não existir outra reserva anteriormente na mesma data.

A autorização será sempre do administrador.

---

## RN-104 — Apenas uma reserva por dia

A Laje do Modesto aceitará somente uma reserva por dia.

Essa decisão foi tomada para garantir tempo adequado para limpeza, organização e preparação do espaço.

---

## RN-105 — Horário de início e duração

O início da festa deve ser em **hora cheia, entre 08:00 e 21:00**.

A duração base é de **8 horas**. O cliente pode contratar horas extras, desde que o término continue sendo, no máximo, às 05:00 da manhã seguinte.

---

# RN-200 — Regras de Pagamento

## RN-201 — Pagamento obrigatório

Toda reserva deverá ser paga integralmente.

Não existirão pagamentos parciais.

---

## RN-202 — Tempo para pagamento

Após realizar uma reserva, o cliente terá **30 minutos** para concluir o pagamento.

Após esse prazo, a reserva será cancelada automaticamente e a data ficará disponível novamente.

---

## RN-203 — Formas de pagamento

O sistema aceitará:

* PIX
* Cartão

---

## RN-204 — Reservas gratuitas

O administrador poderá criar reservas sem cobrança de pagamento.

Essa funcionalidade será utilizada para eventos particulares, familiares ou promocionais.

---

## RN-205 — Caução

Não será exigido caução.

A confirmação do pagamento integral será suficiente para validar a reserva.

---

## RN-206 — Cancelamento

Só reservas **confirmadas** e de **data futura** podem ser canceladas, e somente pelo próprio cliente logado.

* **Até 7 dias antes do evento:** o cancelamento é automático, sem taxa, com reembolso integral do valor pago.
* **Com menos de 7 dias:** é cobrada taxa de **20% do valor total** da reserva. O pedido fica em `CANCELAMENTO_SOLICITADO` e depende da aprovação do administrador.

A taxa e o valor a devolver são calculados no momento do pedido e guardados na reserva. Antes de confirmar, o cliente vê esses valores.

Enquanto o pagamento online não estiver integrado, a devolução do dinheiro é feita manualmente.

---

## RN-207 — Alteração de data e horário

Só reservas **confirmadas** e de **data futura** podem ter alteração solicitada, e somente pelo próprio cliente logado.

* A duração contratada (8 horas + horas extras) é mantida; quem calcula o novo término é o sistema.
* O novo início segue a RN-105 e o término não pode passar das 05:00.
* O novo horário não pode conflitar com outra reserva.
* Enquanto o pedido está pendente, o **horário original continua bloqueado** para outros clientes.
* O administrador aprova ou rejeita. Na aprovação, o sistema confere de novo se o horário continua livre.

---

# RN-300 — Regras do Cliente

## RN-301 — Capacidade

A capacidade máxima da Laje do Modesto será de **130 pessoas**.

O sistema deverá impedir reservas que ultrapassem esse limite quando houver controle da quantidade de convidados.

---

## RN-302 — Som

Será permitida a utilização de equipamentos de som durante todo o período da reserva.

---

## RN-303 — Bebidas e alimentos

O cliente poderá levar livremente alimentos e bebidas.

O sistema não realizará controle desses itens.

---

## RN-304 — Consulta da reserva

A consulta pública, somente leitura, utiliza:

* CPF
* Código da reserva

Não é necessário criar conta ou realizar login para consultar. **Cancelar e alterar exigem login** (RN-500).

---

# RN-400 — Regras Administrativas

## RN-401 — Administrador

O sistema possuirá apenas um administrador.

Esse administrador será o proprietário da Laje do Modesto.

---

## RN-402 — Datas bloqueadas

O administrador poderá bloquear datas por qualquer motivo, como:

* Manutenção
* Feriados
* Eventos particulares
* Reformas
* Qualquer outro motivo operacional

Datas bloqueadas não poderão ser reservadas pelos clientes.

---

# RN-500 — Regras da Conta do Cliente

## RN-501 — Conta opcional

O cliente pode reservar sem criar conta. A conta é necessária para cancelar ou alterar reservas pelo sistema.

## RN-502 — Cadastro com confirmação de e-mail

O cadastro pede nome, e-mail, CPF e telefone. O sistema envia um link ao e-mail informado, válido por **24 horas** e de **uso único**. A conta só é criada, e a senha só é escolhida, depois que o cliente abre o link.

## RN-503 — Login

O login é feito com **e-mail e senha**. Contas do administrador não entram pela Área do Cliente.

## RN-504 — Reservas anteriores

Se o cliente já reservou como visitante com o mesmo e-mail, a conta passa a ser dele e essas reservas aparecem na Área do Cliente. Como o e-mail foi confirmado, ninguém consegue "pegar" reservas de outra pessoa criando uma conta.

## RN-505 — CPF e e-mail

Um CPF que já pertence a um cliente com outro e-mail não pode ser usado em um novo cadastro.

## RN-506 — Recuperação de senha

O cliente pede um link por e-mail, válido por **1 hora** e de **uso único**. Ao criar a nova senha, todos os logins abertos são encerrados.

## RN-507 — Privacidade

Cada cliente só vê e age sobre as próprias reservas. O sistema responde da mesma forma exista ou não uma conta com o e-mail informado, para não revelar quem é cliente.

## RN-508 — Limites de tentativas

Cadastro, login, confirmação e recuperação de senha têm limite de tentativas por hora, para dificultar abusos.

---

# Observações

Toda nova funcionalidade implementada deverá respeitar as regras deste documento.

Caso uma nova regra seja criada futuramente, este documento deverá ser atualizado antes da implementação da funcionalidade correspondente.

---

**Versão:** 1.1

**Status:** Em desenvolvimento