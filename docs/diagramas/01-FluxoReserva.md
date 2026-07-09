# Fluxo da Reserva

## Objetivo

Este diagrama representa o fluxo principal do sistema para realização de uma reserva.

```text
Cliente
   │
   ▼
Acessa o site
   │
   ▼
Visualiza informações da Laje
   │
   ▼
Escolhe a data
   │
   ▼
Seleciona horário
   │
   ▼
Informa os dados pessoais
   │
   ▼
Escolhe adicionais (opcional)
   │
   ▼
Aplica cupom (opcional)
   │
   ▼
Sistema calcula o valor total
   │
   ▼
Escolhe forma de pagamento
   │
   ├── PIX
   └── Cartão
   │
   ▼
Pagamento aprovado
   │
   ▼
Reserva confirmada
   │
   ▼
Sistema gera código da reserva
   │
   ▼
Cliente consulta quando desejar utilizando:
• CPF
• Código da Reserva
```
