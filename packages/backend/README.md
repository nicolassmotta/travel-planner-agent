# 🤖 Backend - Travel Planner AI Agent

Este é o servidor backend do Travel Planner. É uma API construída em **FastAPI** que serve como interface para um agente de IA desenvolvido com o **Google Agent Development Kit (ADK)**.

O agente coordena múltiplas ferramentas (APIs externas) para agregar dados de viagens e o modelo Gemini sintetiza esses dados num plano de viagem coerente.

## 🛠️ Tecnologias

* **Framework**: FastAPI
* **Servidor**: Uvicorn
* **Core de IA**: Google Agent Development Kit (ADK)
* **Modelo LLM**: `gemini-2.5-flash` (configurado em `agent.yaml`)
* **Dependências**: `google-generativeai`, `serpapi`, `requests`, `python-dotenv`

## 🌐 Endpoints da API

### `POST /generate-plan`

Este é o endpoint principal que recebe os detalhes da viagem e retorna o plano completo gerado pela IA.

**Request Body** (`application/json`):

```json
{
  "origin": "São Paulo",
  "destination": "Paris",
  "departureDate": "2025-12-10",
  "returnDate": "2025-12-20",
  "totalBudget": "5000",
  "nightlyBudget": "300",
  "preferences": "Gosto de museus, história e boa gastronomia."
}
```

**Success Response** (200 OK):

```json
{
  "plan": "### ✈️ **Opções de Voos**\n- Voo X... \n\n### 🏨 **Opções de Hotéis**\n- Hotel Y..."
}
```

**Error Response** (500 Internal Server Error):

```json
{
  "error": "Mensagem de erro detalhada..."
}
```

## ⚙️ Configuração Local

### 1. Navegue até à Pasta

```bash
cd packages/backend
```

### 2. Ambiente Virtual

Recomenda-se vivamente o uso de um ambiente virtual:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.\.venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Variáveis de Ambiente

Crie um ficheiro `.env` na raiz desta pasta (`packages/backend/`) e adicione as suas chaves de API. O ficheiro `.gitignore` já está configurado para ignorá-lo.

```ini
# .env

# Chave de API do Google AI Studio (para o Gemini)
GOOGLE_API_KEY=SUA_CHAVE_GOOGLE_AI_AQUI

# Chave de API do SerpApi (para Google Search, Flights, Hotels)
SERPAPI_API_KEY=SUA_CHAVE_SERPAPI_AQUI
```

## ▶️ Executar o Servidor

Com o ambiente virtual ativado e o `.env` configurado, inicie o servidor FastAPI:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000/docs` para visualizar a documentação interativa do Swagger.