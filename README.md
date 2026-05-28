# MindTrack — Backend (FastAPI)

Backend REST para monitoramento de burnout acadêmico. Esta API foi construída com **FastAPI**, **SQLAlchemy** e arquitetura limpa (Clean Architecture), separando domínio puro, casos de uso e infraestrutura.

---

## ✨ Visão geral

- **Propósito:** registrar humor, sono, atividades acadêmicas, alimentação, exercícios e interações sociais para calcular um score de estresse e gerar alertas de burnout.
- **Stack:** Python 3.12, FastAPI, SQLAlchemy, Pydantic, JWT, bcrypt.
- **Arquitetura:** `src/domain` (domínio), `src/application` (casos de uso) e `src/infrastructure` (adaptadores).
- **Execução local:** `uvicorn src.main:app --host 0.0.0.0 --port 3000`
- **Docs auto-gerados:** `http://localhost:3000/docs`

---

## 📁 Estrutura principal

```
src/
├── application/               # Casos de uso e serviços da aplicação
├── config/                    # Carregamento de variáveis de ambiente
├── domain/                    # Regras de negócio e entidades do domínio
└── infrastructure/            # Adapters: HTTP, persistência e segurança
```

---

## 🚀 Como rodar localmente

### Pré-requisitos

- Python 3.11 ou 3.12
- Git

### 1. Criar ambiente virtual

Windows:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` e defina um valor seguro para `JWT_SECRET`.

### 4. Subir a API

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 3000
```

A API ficará disponível em `http://localhost:3000` e a documentação em `http://localhost:3000/docs`.

---

## 🐳 Rodando com Docker

### Usando Docker

```bash
docker build -t mindtrack-backend .
docker run --rm -p 3000:3000 --env-file .env mindtrack-backend
```

### Usando Docker Compose

```bash
docker compose up --build
```

> O contêiner expõe a aplicação em `http://localhost:3000`.

---

## ☁️ Implantação em servidor

### Opção 1 — Servidor Linux com Docker

1. Copie o projeto para o servidor.
2. Crie `.env` com as variáveis de configuração.
3. Execute:
```bash
docker compose up -d --build
```
4. Verifique logs:
```bash
docker compose logs -f
```

### Opção 2 — Servidor Linux sem Docker

1. Instale Python 3.12.
2. Crie e ative venv.
3. Instale dependências:
```bash
pip install -r requirements.txt
```
4. Defina variáveis de ambiente ou use `.env`.
5. Execute com `uvicorn`:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 3000
```
6. Para produção, use um process manager como `systemd` ou `supervisor`.

---

## 🔧 Configuração de ambiente

O `.env.example` já informa todas as variáveis necessárias.

- `JWT_SECRET` — segredo obrigatório
- `JWT_ALGORITHM` — `HS256`
- `JWT_EXPIRE_MINUTES` — tempo de expiração do token
- `DATABASE_URL` — padrão `sqlite:///./mindtrack.db` ou PostgreSQL
- `API_TITLE`, `API_VERSION`, `DEBUG`
- `CORS_ORIGINS` — origens permitidas

---

## 📌 Endpoints principais

### Autenticação
- `POST /api/auth/register` — cadastro de usuário
- `POST /api/auth/login` — login com JWT
- `GET /api/auth/me` — dados do usuário autenticado

### Registros
- `POST /api/registros/humor`
- `POST /api/registros/sono`
- `POST /api/registros/atividades-academicas`
- `POST /api/registros/alimentacao`
- `POST /api/registros/atividade-fisica`
- `POST /api/registros/interacao-social`

### Estresse e histórico
- `GET /api/estresse/score?data=YYYY-MM-DD`
- `GET /api/estresse/historico?dias=7`

### Alertas
- `GET /api/alertas/`
- `PATCH /api/alertas/{id}/lido`

---

## ✅ Testes

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

## 📌 Notas importantes

- A aplicação usa `Settings.from_env()` para ler variáveis de ambiente.
- Se `JWT_SECRET` não existir, a aplicação não inicia.
- O backend já cria o banco SQLite automaticamente ao iniciar.

---

## 🌟 Arquitetura e qualidade

- Camada de domínio isolada em `src/domain`
- Casos de uso em `src/application`
- Infraestrutura injetada via container em `src/infrastructure`
- Aplicação pronta para rodar localmente e em servidor via Docker

---

## 🛠️ Arquivos adicionados

- `Dockerfile` — build da imagem da API
- `docker-compose.yml` — execução em contêiner com `.env`
- `.dockerignore` — evita arquivos não necessários na imagem
