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
* Gerenciar autenticação (administrador e clientes).
* Enviar e-mails de confirmação de cadastro e de recuperação de senha.
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
* Contas de usuário, cadastros pendentes de confirmação e pedidos de nova senha.

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

Administrador e clientes usam Token Authentication, com permissões separadas:

* O painel administrativo só aceita contas de administrador.
* A Área do Cliente só aceita contas de cliente (conta ativa, que não é da equipe e está ligada a um cadastro de cliente).
* A reserva pode ser feita sem login. Consultar por CPF e código também não exige login, mas essa consulta é somente leitura.
* Cancelar e alterar exigem login, e o backend confere que a reserva pertence ao cliente logado.

Os links enviados por e-mail (confirmar cadastro e nova senha) usam tokens de uso único e com validade; no banco fica apenas o hash do token.

---

# Organização do Projeto

backend/

* clientes
* reservas (regras de negócio em `regras.py`, agenda em `disponibilidade.py`, ações em `acoes.py`)
* users (Área do Cliente: cadastro, login, senha, minhas reservas)
* pagamentos
* adicionais
* cupons
* configuracao_laje, configuracoes, dias_bloqueados

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

Versão: 1.1

Status: Em desenvolvimento