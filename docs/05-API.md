# API REST

# Laje do Modesto Reservas

## Objetivo

Este documento descreve os endpoints da API REST do sistema **Laje do Modesto Reservas**.

A API é responsável por realizar toda a comunicação entre o Frontend e o Backend.

Todas as respostas são retornadas no formato **JSON**.

---

# URL Base

```
http://127.0.0.1:8000/api/
```

Em produção:

```
https://seudominio.com/api/
```

---

# Autenticação

As rotas administrativas e as da Área do Cliente utilizam:

* Token Authentication

Após o login, o administrador ou o cliente recebe um Token que deve ser enviado no cabeçalho `Authorization: Token <token>`. As permissões são separadas: o token de cliente não funciona nas rotas administrativas, e o de administrador não funciona na Área do Cliente.

---

# Clientes

## Listar Clientes

```
GET /clientes/
```

---

## Cadastrar Cliente

```
POST /clientes/
```

---

## Consultar Cliente

```
GET /clientes/{id}/
```

---

## Atualizar Cliente

```
PUT /clientes/{id}/
```

---

## Excluir Cliente

```
DELETE /clientes/{id}/
```

---

# Reservas

## Listar Reservas

```
GET /reservas/
```

---

## Criar Reserva

```
POST /reservas/
```

---

## Consultar Reserva

```
GET /reservas/{id}/
```

---

## Atualizar Reserva

```
PUT /reservas/{id}/
```

---

## Excluir Reserva

```
DELETE /reservas/{id}/
```

---

# Consulta Pública (somente leitura)

Consultar reserva utilizando:

* CPF
* Código da Reserva

```
POST /consultar-reserva/
```

Retorna código, data, horário e status. Não permite cancelar nem alterar.

---

# Área do Cliente

Rotas sob `/cliente/`. As rotas de **cadastro, confirmação, login e senha** são públicas. As demais exigem o cabeçalho:

```
Authorization: Token <token recebido no login>
```

O token de um cliente não acessa rotas administrativas.

## Cadastro (passo 1)

```
POST /cliente/cadastro/
```

Corpo: `nome`, `email`, `cpf`, `telefone`. Envia um link por e-mail (válido por 24 h). Nenhuma conta é criada ainda. A resposta é a mesma exista ou não uma conta com o e-mail.

## Confirmar cadastro (passo 2)

```
POST /cliente/confirmar-cadastro/
```

Corpo: `token` (do link) e `senha`. Cria a conta e liga ao cliente. Se o cliente já reservou como visitante com o mesmo e-mail, as reservas passam a aparecer na conta.

## Login

```
POST /cliente/login/
```

Corpo: `email` e `senha`. Retorna `token` e os dados do cliente. Erro de login responde sempre `401` com a mesma mensagem.

## Logout

```
POST /cliente/logout/
```

Apaga o token do cliente.

## Meus dados

```
GET /cliente/meus-dados/
PATCH /cliente/meus-dados/
```

O `PATCH` aceita apenas `nome` e `telefone`. O CPF é devolvido parcialmente escondido.

## Minhas reservas

```
GET /cliente/minhas-reservas/
GET /cliente/minhas-reservas/{codigo}/
```

Cada reserva traz `pode_cancelar` e `pode_alterar` e, quando cabível, `previa_cancelamento` com `dentro_do_prazo`, `taxa` e `reembolso`. Reserva de outra pessoa responde `404`, igual a um código inexistente.

## Cancelar reserva

```
POST /cliente/minhas-reservas/{codigo}/cancelar/
```

Até 7 dias antes: status `CANCELADA`, sem taxa. Depois: status `CANCELAMENTO_SOLICITADO`, taxa de 20%, aguardando o administrador.

## Alterar reserva

```
POST /cliente/minhas-reservas/{codigo}/alterar/
```

Corpo: `nova_data` (AAAA-MM-DD) e `novo_horario_inicio` (HH:MM). O término é calculado pelo servidor. Status passa a `ALTERACAO_SOLICITADA`.

## Esqueci minha senha

```
POST /cliente/esqueci-senha/
POST /cliente/redefinir-senha/
```

O primeiro recebe `email` e envia um link (válido por 1 h). O segundo recebe `token` e `senha`, troca a senha e encerra os logins abertos.

---

# Alterações (administrador)

Aprovar:

```
POST /aprovar-alteracao/
```

Rejeitar:

```
POST /rejeitar-alteracao/
```

---

# Cancelamentos (administrador)

Aprovar:

```
POST /aprovar-cancelamento/
```

Rejeitar:

```
POST /rejeitar-cancelamento/
```

Os pedidos de cancelamento e alteração são feitos pela Área do Cliente. As antigas rotas públicas `/solicitar-alteracao/` e `/solicitar-cancelamento/` foram removidas.

---

# Login Administrativo

```
POST /admin-login/
```

Retorna:

* Token
* Nome do administrador

---

# Dashboard

```
GET /dashboard/
```

Retorna:

* Total de reservas
* Confirmadas
* Pendentes
* Cancelamentos
* Alterações

---

# Cupons

```
GET /cupons/
POST /cupons/
PUT /cupons/{id}/
DELETE /cupons/{id}/
```

---

# Adicionais

```
GET /adicionais/
POST /adicionais/
PUT /adicionais/{id}/
DELETE /adicionais/{id}/
```

---

# Pagamentos

```
GET /pagamentos/
POST /pagamentos/
```

---

# Códigos HTTP

A API utiliza os seguintes códigos de resposta:

| Código | Significado              |
| ------ | ------------------------ |
| 200    | Sucesso                  |
| 201    | Criado com sucesso       |
| 400    | Requisição inválida      |
| 401    | Não autenticado          |
| 403    | Acesso negado            |
| 404    | Não encontrado           |
| 429    | Muitas tentativas        |
| 500    | Erro interno do servidor |

---

# Padrão das Respostas

Sucesso:

```json
{
    "mensagem": "Operação realizada com sucesso."
}
```

Erro:

```json
{
    "erro": "Descrição do erro."
}
```

---

**Versão:** 1.1

**Status:** Em desenvolvimento