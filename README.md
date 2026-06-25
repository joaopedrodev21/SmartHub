# SmartHub-Django

Sistema **CRM** desenvolvido com **Django** e **Django REST Framework** como projeto de seleção para o **NADIC (IFRN)**.

---

## 📋 Sobre o Projeto

CRM (Customer Relationship Management) para gerenciamento de produtos, estoque e vendas de uma empresa. O sistema conta com:

- **Interface Web** (Django Templates) — CRUD de produtos, registro de vendas, dashboard
- **API REST** (Django REST Framework) — Endpoints protegidos com JWT

---

## 🚀 Funcionalidades

### Interface Web
- Cadastro, edição e remoção de produtos
- Controle de estoque
- Registro de vendas (atualiza estoque automaticamente)
- Dashboard com faturamento da empresa
- Autenticação de usuários

### API REST
- Registro e login de usuários (JWT)
- CRUD completo de produtos (somente autenticados)
- Detalhes do produto com estoque
- Faturamento da empresa (somente o dono)

---

## Tecnologias

- Python 3
- Django 5
- Django REST Framework
- SQLite (desenvolvimento) / PostgreSQL (produção)
- SimpleJWT (autenticação)

---

## Estrutura do Projeto

```
SmartHub-Django/
├── config/                   # Configurações do projeto Django
├── apps/
│   ├── accounts/            # Autenticação e perfil de usuário
│   ├── products/            # Gerenciamento de produtos
│   ├── sales/               # Registro de vendas
│   └── customers/           # Clientes
├── templates/               # HTMLs do projeto
├── static/                  # CSS, JS, imagens
├── media/                   # Uploads
├── manage.py
└── requirements.txt
```

**Guia completo de estudo e implementação** → [`GUIDE.md`](./GUIDE.md)

---

## ⚙️ Como Rodar o Projeto

```bash
# 1. Clone o repositório
git clone https://github.com/joaopedrodev21/SmartHub.git
cd SmartHub-Django

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute as migrações
python manage.py migrate

# 5. Crie um superusuário (opcional)
python manage.py createsuperuser

# 6. Inicie o servidor
python manage.py runserver
```

---

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/register/` | Criar conta |
| POST | `/api/auth/login/` | Login (JWT) |
| GET | `/api/products/` | Listar produtos |
| POST | `/api/products/` | Cadastrar produto |
| GET | `/api/products/{id}/` | Detalhes do produto |
| PUT | `/api/products/{id}/` | Editar produto |
| DELETE | `/api/products/{id}/` | Remover produto |
| GET | `/api/sales/` | Listar vendas |
| POST | `/api/sales/` | Realizar venda |
| GET | `/api/company/revenue/` | Faturamento (dono) |

---

## Autor

**João Pedro** — IFRN

Projeto de seleção para o **NADIC** — Grupo de Pesquisa em Programação do IFRN.