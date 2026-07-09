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

As rotas administrativas utilizam:

* Token Authentication

Após realizar login, o administrador receberá um Token que deverá ser enviado nas próximas requisições.

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

# Consulta do Cliente

Consultar reserva utilizando:

* CPF
* Código da Reserva

```
POST /consultar-reserva/
```

---

# Alterações

Solicitar alteração:

```
POST /solicitar-alteracao/
```

---

Administrador aprova:

```
POST /aprovar-alteracao/
```

---

Administrador rejeita:

```
POST /rejeitar-alteracao/
```

---

# Cancelamentos

Solicitar cancelamento:

```
POST /solicitar-cancelamento/
```

---

Administrador aprova:

```
POST /aprovar-cancelamento/
```

---

Administrador rejeita:

```
POST /rejeitar-cancelamento/
```

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

**Versão:** 1.0

**Status:** Em desenvolvimento
