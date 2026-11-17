# Laje do Modesto Reservas

## Visão do Projeto

### Sobre o Projeto

O **Laje do Modesto Reservas** é um sistema web desenvolvido para automatizar o processo de reservas do espaço de eventos Laje do Modesto.

O projeto nasceu com o objetivo de substituir o processo manual de atendimento realizado por mensagens no WhatsApp, oferecendo uma plataforma simples, rápida e segura para clientes e para o administrador do espaço.

Além de atender uma necessidade real do negócio, este projeto também faz parte do desenvolvimento acadêmico e profissional do desenvolvedor, sendo construído seguindo boas práticas de Engenharia de Software, Arquitetura de Sistemas e Desenvolvimento Web.

---

# Objetivo

Criar um sistema moderno, seguro e responsivo que permita ao cliente realizar reservas de forma totalmente online, enquanto o administrador possui controle completo sobre datas, pagamentos, alterações e cancelamentos.

---

# Público-alvo

O sistema é destinado para pessoas interessadas em alugar o espaço da Laje do Modesto para eventos particulares.

O cliente pode fazer uma reserva sem criar conta. Para cancelar ou alterar uma reserva pelo sistema, ele cria uma conta (com confirmação por e-mail) e acessa a **Área do Cliente**.

O administrador será exclusivamente o proprietário da Laje do Modesto.

---

# Objetivos do Sistema

* Automatizar o processo de reservas.
* Diminuir o atendimento manual pelo WhatsApp.
* Permitir consultas de reservas utilizando CPF e código da reserva.
* Oferecer uma Área do Cliente, com login, onde ele vê as próprias reservas e pede cancelamento ou alteração.
* Aplicar automaticamente a política de cancelamento (gratuito até 7 dias antes; taxa depois disso).
* Centralizar o gerenciamento das reservas.
* Facilitar pagamentos online.
* Disponibilizar uma interface amigável para dispositivos móveis.
* Tornar o processo de reserva simples para qualquer pessoa.

---

# Tecnologias

## Backend

* Python
* Django
* Django REST Framework

## Frontend

* HTML5
* CSS3
* JavaScript

## Banco de Dados

* SQLite (desenvolvimento)
* PostgreSQL (produção)

---

# Filosofia do Projeto

Este sistema está sendo desenvolvido como um software profissional.

Cada funcionalidade será planejada antes da implementação, documentada e versionada utilizando Git e GitHub.

O objetivo é entregar um produto preparado para utilização em ambiente real.

---

# Visão de Futuro

O projeto será expandido com novas funcionalidades, incluindo:

* Calendário inteligente.
* Dashboard financeiro.
* Pagamentos via PIX e Cartão.
* Relatórios administrativos.
* Sistema de cupons.
* Gestão de adicionais.
* Área administrativa completa.
* Deploy em ambiente de produção.
* Integração com serviços de pagamento.

---

# Estado Atual

Atualmente o sistema já possui:

* Cadastro de clientes.
* Cadastro de reservas, com regras de horário e proteção contra reservas simultâneas.
* Consulta pública de reservas (CPF + código), somente leitura.
* Área do Cliente: cadastro com confirmação por e-mail, login, recuperação de senha, minhas reservas, alteração de dados.
* Cancelamento pela Área do Cliente: automático até 7 dias antes do evento; depois, taxa de 20% com aprovação do administrador.
* Solicitação de alteração de data e horário pela Área do Cliente, com aprovação do administrador.
* Painel administrativo.
* Dashboard.
* Login administrativo.
* Autenticação por Token.
* Busca de reservas.
* Layout responsivo inicial.

Ainda não implementado: pagamento online (Mercado Pago, PIX e cartão), expiração automática de reservas sem pagamento, envio de notificações por e-mail sobre aprovações e a publicação em produção.

---

**Versão do Documento:** 1.1

**Projeto:** Laje do Modesto Reservas

**Status:** Em desenvolvimento