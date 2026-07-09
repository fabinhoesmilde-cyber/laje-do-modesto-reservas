# Arquitetura do Sistema

# Laje do Modesto Reservas

## Objetivo

Este documento descreve a arquitetura utilizada no desenvolvimento do sistema Laje do Modesto Reservas.

O objetivo é manter o projeto organizado, escalável e de fácil manutenção.

---

# Arquitetura Geral

O sistema utiliza uma arquitetura cliente-servidor.

A comunicação entre o Frontend e o Backend acontece através de uma API REST desenvolvida em Django REST Framework.

```text
Cliente
    │
    ▼
Frontend (HTML, CSS e JavaScript)
    │
    ▼
API REST (Django REST Framework)
    │
    ▼
Banco de Dados
```

---

# Frontend

Responsável por toda a interface do usuário.

Tecnologias:

* HTML5
* CSS3
* JavaScript

Responsabilidades:

* Exibir telas.
* Validar informações simples.
* Consumir a API.
* Mostrar mensagens ao usuário.

O Frontend nunca acessa o banco de dados diretamente.

---

# Backend

Responsável por toda a regra de negócio.

Tecnologias:

* Python
* Django
* Django REST Framework

Responsabilidades:

* Validar dados.
* Gerenciar reservas.
* Gerenciar clientes.
* Gerenciar pagamentos.
* Gerenciar autenticação.
* Aplicar as regras de negócio.

Toda decisão importante acontece no Backend.

---

# Banco de Dados

Durante o desenvolvimento:

SQLite.

Em produção:

PostgreSQL.

O banco armazenará:

* Clientes.
* Reservas.
* Pagamentos.
* Cupons.
* Adicionais.
* Status.
* Tokens.

---

# Comunicação

Toda comunicação acontecerá utilizando JSON.

Exemplo:

Cliente envia:

{
"cpf": "12345678900",
"codigo_reserva": "ABC123"
}

Servidor responde:

{
"status": "CONFIRMADA"
}

---

# Segurança

O painel administrativo será protegido utilizando Token Authentication.

Clientes não precisarão realizar login.

Somente o administrador possuirá autenticação.

---

# Organização do Projeto

backend/

* clientes
* reservas
* pagamentos
* adicionais
* cupons

frontend/

* páginas HTML
* CSS
* JavaScript

docs/

* documentação

database/

* arquivos relacionados ao banco de dados

---

# Objetivo da Arquitetura

A arquitetura foi planejada para permitir o crescimento do sistema sem necessidade de grandes alterações estruturais.

Novos módulos poderão ser adicionados mantendo a organização do projeto.

---

Versão: 1.0

Status: Em desenvolvimento
