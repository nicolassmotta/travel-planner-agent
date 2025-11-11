# ✈️ Travel Planner AI Agent

Bem-vindo ao Travel Planner, um assistente de viagens inteligente full-stack. Esta aplicação utiliza um agente de IA (Google Gemini) para construir planos de viagem completos e personalizados, integrando dados em tempo real de voos, hotéis, clima e atividades.

## ✨ Funcionalidades Principais

* **Planeamento por IA:** Recebe dados do utilizador (destino, datas, orçamento) e gera um itinerário detalhado em markdown.
* **Streaming de Resposta:** O plano de viagem é exibido em tempo real, token por token, para uma experiência de utilizador instantânea.
* **Dados em Tempo Real:** Integra-se com APIs para buscar:
    * Opções de Voos (SerpApi)
    * Sugestões de Hotéis (SerpApi)
    * Recomendações de Atividades (SerpApi)
    * Previsão do Tempo Histórica (Open-Meteo)
* **Interface Moderna:** Frontend reativo construído em React, TypeScript e shadcn-ui.
* **Gestão de Planos:** Salva os planos de viagem no Local Storage para visualização futura.
* **Exportação:** Permite o download do plano de viagem como PDF.
* **Modo Light/Dark:** Suporte completo para temas.

## 🛠️ Pilha Tecnológica

Este projeto é um monorepo que contém dois pacotes principais:

* **`packages/frontend`**:
    * **Framework**: React 18 com Vite e TypeScript
    * **UI**: shadcn-ui, Tailwind CSS
    * **Formulários**: React Hook Form com Zod para validação
    * **Routing**: React Router
    * **Utilitários**: `jspdf`, `html2canvas` (para exportar PDF), `react-markdown`

* **`packages/backend`**:
    * **Framework**: Python 3 com FastAPI
    * **Core de IA**: Google Agent Development Kit (ADK)
    * **Modelo**: Google Gemini (ex: `gemini-2.5-flash`)
    * **Ferramentas (APIs)**: SerpApi (Google Search/Hotels), Open-Meteo

## 📂 Estrutura do Repositório

```
/travel-planner-agent
├── packages/
│   ├── backend/  (Servidor FastAPI + Agente ADK)
│   └── frontend/ (Aplicação React/Vite)
├── .gitignore    (Gitignore principal)
├── README.md     (Este ficheiro)
└── LICENSE
```

## 🚀 Como Executar o Projeto

Para executar o projeto completo, precisará de iniciar o backend e o frontend em terminais separados.

### 1. Backend

Instruções detalhadas no **[README do Backend](./packages/backend/README.md)**.

```bash
# Navegue para a pasta do backend
cd packages/backend

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate # (ou .\.venv\Scripts\activate no Windows)

# Instale as dependências
pip install -r requirements.txt

# Crie um ficheiro .env com as suas chaves de API
# (Pode copiar .env.example se existir, ou criar um novo)
nano .env # (Adicione GOOGLE_API_KEY e SERPAPI_API_KEY)

# Inicie o servidor
uvicorn main:app --reload --port 8000
```

### 2. Frontend

Instruções detalhadas no **[README do Frontend](./packages/frontend/README.md)**.

```bash
# Num novo terminal, navegue para a pasta do frontend
cd packages/frontend

# Crie um ficheiro .env
nano .env # (Adicione VITE_API_URL=http://localhost:8000)

# Instale as dependências
npm install # (ou pnpm install / bun install)

# Inicie o servidor de desenvolvimento
npm run dev
```

A aplicação estará disponível em `http://localhost:8080`.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.