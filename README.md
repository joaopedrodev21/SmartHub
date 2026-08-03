# SmartHub-Django

Sistema [CRM](https://pt.wikipedia.org/wiki/Gest%C3%A3o_de_relacionamento_com_o_cliente) (Customer Relationship Management) desenvolvido com Django e Django REST Framework, criado como projeto de seleção para o NADIC (IFRN).

---

## Sobre o Projeto

O SmartHub CRM é um sistema de gestão empresarial que permite cadastrar e gerenciar produtos, controlar estoque, registrar vendas vinculadas a clientes e acompanhar o faturamento total da empresa em um dashboard. O sistema conta com:

- Interface Web (Django Templates) — CRUD de produtos, clientes e vendas, dashboard gerencial e autenticação
- API REST (Django REST Framework) — Endpoints protegidos com autenticação JWT
- Multi-empresa (tenant isolation) — cada usuário visualiza e gerencia apenas os dados da sua empresa

---

## Funcionalidades

### Interface Web

- CRUD de produtos (criar, listar, editar, excluir), com nome, descrição, preço, estoque, categoria e marca
- CRUD de clientes, com nome, email, telefone e endereço
- Registro de vendas vinculado a um cliente, com atualização automática do estoque e do faturamento
- Dashboard com métricas: total de produtos, unidades em estoque, faturamento e total de vendas, além das últimas vendas
- Autenticação de usuários: cadastro, login por email, logout e recuperação de senha
- Página de perfil com edição de dados pessoais (nome, email) e da empresa (nome, telefone, endereço)
- Isolamento por empresa: todos os dados (produtos, clientes, vendas e dashboard) são filtrados pela empresa do usuário logado
- Mensagens de feedback (sucesso/erro) em todas as operações de CRUD
- Interface moderna com Bootstrap 5 e ícones Lucide

### API REST

- Registro de usuários (cria empresa automaticamente)
- Login de usuários (retorna tokens JWT)
- CRUD completo de produtos (somente para usuários autenticados)
- Detalhes do produto com estoque
- Faturamento da empresa (somente o dono da empresa pode acessar)
- Visualização via ViewSets e Routers (DefaultRouter)

---

## Tecnologias

- Python 3
- Django 6
- Django REST Framework
- djangorestframework-simplejwt (autenticação JWT)
- SQLite (desenvolvimento) / PostgreSQL (produção)
- Bootstrap 5 e Lucide (interface)

---

## Estrutura do Projeto

```
SmartHub-Django/
├── config/                   # Configurações do projeto Django
├── apps/
│   ├── api/                 # URLs da API REST
│   ├── products/            # Gerenciamento de produtos e API
│   ├── sales/               # Registro de vendas (com signals)
│   └── customers/           # Clientes e empresas
├── templates/               # HTMLs do projeto
├── static/                  # CSS e JS
├── manage.py
└── requirements.txt
```

---

## Como Rodar o Projeto

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

# 5. Crie um superusuário (opcional, para o admin)
python manage.py createsuperuser

# 6. Inicie o servidor
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

---

## Endpoints da API

| Método | Endpoint                    | Descrição                          | Autenticação |
|--------|-----------------------------|------------------------------------|--------------|
| POST   | `/api/auth/register/`       | Criar conta (cria empresa)          | Pública      |
| POST   | `/api/auth/login/`          | Login (retorna tokens JWT)          | Pública      |
| GET    | `/api/products/`            | Listar produtos da empresa          | JWT          |
| POST   | `/api/products/`            | Cadastrar produto                   | JWT          |
| GET    | `/api/products/{id}/`       | Detalhes do produto                 | JWT          |
| PUT    | `/api/products/{id}/`       | Editar produto                      | JWT          |
| PATCH  | `/api/products/{id}/`       | Editar parcialmente o produto       | JWT          |
| DELETE | `/api/products/{id}/`       | Remover produto                     | JWT          |
| GET    | `/api/products/{id}/stock/` | Detalhes do estoque do produto      | JWT          |
| GET    | `/api/company/revenue/`     | Faturamento (somente o dono)        | JWT          |

Para autenticar, envie o token no header:

```
Authorization: Bearer <access_token>
```

---

## Modelagem Principal

- Company: nome, email, dono (User), telefone, endereço, faturamento acumulado
- Product: nome, descrição, preço, estoque, categoria, marca, empresa
- Customer: nome, email, telefone, endereço, empresa
- Sale: produto, cliente, quantidade, preço total, empresa

O campos `company` em Product, Customer e Sale garantem o isolamento por empresa. As vendas vinculam produto e cliente da mesma empresa, e o signal `update_stock_and_revenue` atualiza automaticamente o estoque e o faturamento a cada venda.

---

## Autor

**João Pedro** — IFRN

Projeto de seleção para o **NADIC** — Grupo de Pesquisa em Programação do IFRN.
