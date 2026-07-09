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

Caso o cliente solicite o cancelamento com até **7 dias de antecedência**, terá direito ao reembolso integral do valor pago.

Solicitações realizadas com menos de 7 dias poderão sofrer cobrança conforme a política da Laje do Modesto.

A aprovação final continuará sendo realizada pelo administrador.

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

O cliente consultará sua reserva utilizando:

* CPF
* Código da reserva

Não será necessário criar conta ou realizar login.

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

# Observações

Toda nova funcionalidade implementada deverá respeitar as regras deste documento.

Caso uma nova regra seja criada futuramente, este documento deverá ser atualizado antes da implementação da funcionalidade correspondente.

---

**Versão:** 1.0

**Status:** Em desenvolvimento
