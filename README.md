# ✈️ AgênciaSys: Sistema de Gestão de Viagens e Reservas

> Sistema web desenvolvido para a gestão eficiente de pacotes turísticos, reservas de clientes e controle de disponibilidade, resolvendo os problemas de **overbooking** e falhas operacionais em agências de viagens.

---

## 💡 Contextualização e Desafio

Uma agência de viagens local enfrentava sérios problemas de gestão devido ao controle totalmente **manual** de pacotes e reservas. Isso resultava em *overbooking* frequente, dificuldade de rastreabilidade e falhas na comunicação.

O projeto **AgênciaTour** foi desenvolvido para resolver esses gargalos, oferecendo uma solução **informatizada** para garantir a **integridade dos dados**, a rastreabilidade das operações e a **redução de erros** em um portfólio de produtos turísticos altamente diversificado.

---

## ✨ Funcionalidades Principais

O sistema foi estruturado para suportar o ciclo completo de venda e gestão de viagens:

| Módulo | Descrição | Comandos Chave |
| :--- | :--- | :--- |
| **Cadastro de Pacotes** | Permite registrar informações detalhadas (destino, preço, período, categoria, etc.) com **controle de vagas** (mínima e máxima). | CRUD |
| **Gestão de Reservas** | Registro de novas reservas e processamento de **cancelamentos**, mantendo o status atualizado do pacote. | Entrar, Cancelar |
| **Alerta de Vagas** | Emite **alertas** em casos de **disponibilidade insuficiente** ou excesso de reservas (prevenção de *overbooking*). | Validação |
| **Histórico** | Registra um log completo de todas as operações, garantindo total **rastreabilidade** (quem fez, quando, para qual cliente). | Log de Auditoria |
| **Segurança/Perfis** | **Autenticação de Usuários** com diferenciação de acesso entre perfis de **Administrador** e **Atendente**. | Login, Logout |

---

## 🛠️ Tecnologias Utilizadas

Este projeto é uma aplicação web Full Stack desenvolvida com a seguinte *stack*:

* **Backend:** **Python** com o *framework* **Flask**
* **Frontend:** **HTML5, CSS3, JavaScript**
* **Banco de Dados:** **SQLite** (Base de dados relacional simples e leve)

---

## 🚀 Como Executar o Projeto Localmente

Siga estes passos para configurar e rodar o **AgênciaTour** em sua máquina:

### 1. Pré-requisitos

* Python 3.x instalado.

### 2. Configuração do Ambiente

1.  Clone este repositório:
    ```bash
    git clone [https://github.com/seu-usuario/agenciatour.git](https://github.com/seu-usuario/agenciatour.git)
    cd agenciatour
    ```
2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```
3.  Instale as dependências Python (Flask):
    ```bash
    pip install Flask
    # (Adicione aqui outras dependências do seu projeto, se houver)
    ```

### 3. Rodar o Sistema

Inicie a aplicação Flask:

```bash
python app.py
