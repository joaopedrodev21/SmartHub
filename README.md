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
- Refresh do access token (renovação de sessão via refresh token)
- CRUD completo de produtos (somente para usuários autenticados)
- Detalhes do produto com estoque
- Faturamento da empresa (somente o dono da empresa pode acessar)
- Busca, ordenação e paginação na listagem de produtos
- Visualização via ViewSets e Routers (DefaultRouter)
- **Documentação interativa** da API via Swagger UI/Redoc com `drf-spectacular` (OpenAPI 3)

---

## Tecnologias

- Python 3
- Django 6
- Django REST Framework
- djangorestframework-simplejwt (autenticação JWT)
- drf-spectacular (documentação OpenAPI 3 / Swagger UI / Redoc)
- SQLite (desenvolvimento) / PostgreSQL (produção)
- Bootstrap 5 e Lucide (interface)
- Docker e Docker Compose (containerização)

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
├── Dockerfile               # Definição da imagem do container
├── docker-compose.yml       # Orquestração dos serviços
├── .dockerignore            # Arquivos ignorados na imagem
├── .env                     # Variáveis de ambiente (não versionado)
├── manage.py
└── requirements.txt
```

---

## Como Rodar o Projeto (sem Docker)

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

# 4. Configure o arquivo .env (se ainda não existir)
#    Crie um arquivo .env na raiz com as variáveis de email (ver seção Docker)

# 5. Execute as migrações
python manage.py migrate

# 6. Crie um superusuário (opcional, para o admin)
python manage.py createsuperuser

# 7. Inicie o servidor
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

---

## Como Rodar o Projeto (com Docker)

Certifique-se de ter o **Docker Desktop** instalado e em execução.

### 1. Configure o arquivo `.env`

Crie ou edite o arquivo `.env` na raiz do projeto com as variáveis de ambiente necessárias:

```env
# Email (SMTP do Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=seuemail@gmail.com
EMAIL_HOST_PASSWORD="sua senha de app do gmail"
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL="SmartHub CRM <seuemail@gmail.com>"
```

**Atenção**: valores com espaços (como a senha de app do Gmail) devem ficar entre aspas duplas.

### 2. Construa e suba o container

```bash
docker-compose up --build
```

Isso vai:
- Construir a imagem a partir do `Dockerfile`
- Injetar as variáveis do `.env` via `env_file`
- Rodar as migrações automaticamente
- Iniciar o Django em `0.0.0.0:8000`

### 3. Acesse a aplicação

Abra o navegador em **http://localhost:8000/** (não use `0.0.0.0` no navegador).

### 4. Crie um superusuário (opcional)

Em outro terminal:

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Comandos Docker úteis

| Comando | Descrição |
|---------|-----------|
| `docker-compose up` | Sobe a aplicação (em primeiro plano) |
| `docker-compose up --build` | Constrói a imagem e sobe a aplicação |
| `docker-compose up -d` | Sobe em segundo plano (background) |
| `docker-compose logs -f` | Acompanha os logs em tempo real |
| `docker-compose exec web bash` | Abre um terminal dentro do container |
| `docker-compose exec web python manage.py migrate` | Roda migrações manualmente |
| `docker-compose down` | Para e remove os containers |
| `docker-compose down -v` | Para e remove containers + volume do banco |

---

## Como Testar o Projeto

### Testes automatizados

Rode os testes app por app (a execução conjunta de múltiplos apps pode gerar conflito de módulo `tests` no Python 3.14):

```bash
python manage.py test apps.products -v 1
python manage.py test apps.sales -v 1
python manage.py test apps.customers -v 1
```

**Com Docker:**
```bash
docker-compose exec web python manage.py test apps.products -v 1
docker-compose exec web python manage.py test apps.sales -v 1
docker-compose exec web python manage.py test apps.customers -v 1
```

### Testar o envio de email (SMTP do Gmail)

```bash
python manage.py shell -c "from django.core.mail import send_mail; from django.conf import settings; send_mail('Teste', 'Corpo do email', settings.DEFAULT_FROM_EMAIL, ['destinatario@email.com'], fail_silently=False)"
```

### Testar o fluxo de redefinição de senha

1. Acesse `/accounts/password-reset/`
2. Informe o email de um usuário cadastrado
3. Verifique a chegada do email na caixa de entrada/spam
4. Clique no link e defina uma nova senha

> **Observação**: o Django só envia o email de redefinição se o email informado **pertencer a um usuário cadastrado** no sistema.

### Testar o fluxo completo do CRM

1. Cadastre-se em `/accounts/register/` (cria usuário + empresa automaticamente)
2. Faça login
3. Cadastre um cliente
4. Cadastre um produto
5. Registre uma venda (estoque e faturamento são atualizados automaticamente)
6. Verifique o dashboard

---

## Endpoints da API

| Método | Endpoint                    | Descrição                          | Autenticação |
|--------|-----------------------------|------------------------------------|--------------|
| POST   | `/api/auth/register/`       | Criar conta (cria empresa)          | Pública      |
| POST   | `/api/auth/login/`          | Login (retorna tokens JWT)          | Pública      |
| POST   | `/api/auth/refresh/`        | Renovar o access token              | Refresh Token |
| GET    | `/api/products/`            | Listar produtos da empresa          | JWT          |
| POST   | `/api/products/`            | Cadastrar produto                   | JWT          |
| GET    | `/api/products/{id}/`       | Detalhes do produto                 | JWT          |
| PUT    | `/api/products/{id}/`       | Editar produto                      | JWT          |
| PATCH  | `/api/products/{id}/`       | Editar parcialmente o produto       | JWT          |
| DELETE | `/api/products/{id}/`       | Remover produto                     | JWT          |
| GET    | `/api/products/{id}/stock/` | Detalhes do estoque do produto      | JWT          |
| GET    | `/api/company/revenue/`     | Faturamento (somente o dono)        | JWT          |
| GET    | `/api/docs/`                | Documentação interativa (Swagger UI) | Pública      |
| GET    | `/api/schema/`              | Schema OpenAPI 3                     | Pública      |
| GET    | `/api/schema/redoc/`        | Documentação Redoc                   | Pública      |

### Filtros, Ordenação e Paginação

A listagem de produtos suporta filtro por busca, ordenação e paginação:

| Parâmetro  | Exemplo                                  | Descrição                                            |
|------------|------------------------------------------|------------------------------------------------------|
| `search`   | `/api/products/?search=gamer`            | Busca em nome, descrição, marca e categoria          |
| `ordering` | `/api/products/?ordering=-price`         | Ordena por campo (`-` para decrescente). Campos: `name`, `price`, `stock`, `created_at` |
| `page`     | `/api/products/?page=2`                  | Página da paginação (10 itens por página)            |

A resposta da listagem é paginada no formato:

```json
{
  "count": 15,
  "next": "http://.../api/products/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

Para autenticar, envie o token no header:

```
Authorization: Bearer <access_token>
```

---

## Documentação da API (Swagger)

A API é documentada automaticamente com [drf-spectacular](https://drf-spectacular.readthedocs.io/), que gera um schema OpenAPI 3 e uma interface interativa e navegável para testar os endpoints.

### URLs de documentação

| Página | URL |
|--------|-----|
| **Swagger UI** (interface navegável) | `/api/docs/` |
| Swagger UI (padrão) | `/api/schema/swagger-ui/` |
| Redoc (documentação em coluna única) | `/api/schema/redoc/` |
| Schema OpenAPI 3 (JSON crú) | `/api/schema/` |

Com o servidor rodando (`python manage.py runserver`), acesse **http://127.0.0.1:8000/api/docs/** no navegador.

### Como usar o Swagger (com autenticação JWT)

1. Abra `/api/docs/`
2. Expanda **`POST /api/auth/register/`** (cria usuário + empresa e retorna os tokens) ou **`POST /api/auth/login/`** (se já tiver conta)
3. Copie o valor do token **`access`** retornado
4. Clique no botão **Authorize** (cadeado, no topo da página), cole o token e confirme
5. Teste os endpoints protegidos (produtos, estoque e faturamento) direto pelo botão **"Try it out"**

> O `persistAuthorization` está habilitado, então o token permanece salvo entre as requisições. As respostas de `register`/`login` retornam o par `access`/`refresh`; use `/api/auth/refresh/` para renovar o token quando o `access` expirar.

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