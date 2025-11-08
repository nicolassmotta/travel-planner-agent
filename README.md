# 🤖 Agente de Planejamento de Viagens

Este projeto é um agente de conversação inteligente, construído com o **Google Agent Development Kit (ADK)**, capaz de planejar viagens personalizadas. O agente utiliza APIs reais para buscar voos, hotéis, atividades e a previsão do tempo com base nas solicitações do usuário.

## 🚀 Funcionalidades

O agente pode processar um prompt de linguagem natural (ex: "Planeje uma viagem para Paris de 10 a 15 de dezembro com foco cultural e orçamento de R$500 por noite") e usar as seguintes ferramentas:

  * **Busca de Voos:** Encontra opções de voos usando a API Serper.dev (Google Search).
  * **Busca de Hotéis:** Encontra acomodações usando a API Serper.dev (Google Search), filtrando por sites de reserva.
  * **Sugestão de Atividades:** Recomenda atrações turísticas (culturais, gastronômicas, etc.) usando a API Serper.dev.
  * **Previsão do Tempo:** Obtém a previsão do tempo para os próximos dias no destino usando a API gratuita Open-Meteo.

## 🛠️ Tecnologias Utilizadas

  * **Core:** Python 3, Google Agent Development Kit (ADK)
  * **Dependências Principais:** (veja `requirements.txt`)
      * `google-generativeai` (Para o modelo Gemini)
      * `python-dotenv` (Para gerenciamento de variáveis de ambiente)
      * `requests` (Para realizar chamadas de API)
  * **APIs Externas:**
      * Google AI (Gemini)
      * Serper.dev (Google Search API para voos, hotéis e atividades)
      * Open-Meteo (Previsão do Tempo)

## ⚙️ Configuração e Instalação

Siga os passos abaixo para configurar e executar o projeto localmente.

### 1\. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/travel-planner-agent.git
cd travel-planner-agent
```

### 2\. Criar Ambiente Virtual e Instalar Dependências

É altamente recomendado usar um ambiente virtual:

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.\.venv\Scripts\activate
# Ativar (Linux/macOS)
source .venv/bin/activate

# Instalar pacotes
pip install -r requirements.txt
```

### 3\. Configurar Variáveis de Ambiente

O projeto utiliza um arquivo `.env` para gerenciar chaves de API. O arquivo `.gitignore` já está configurado para ignorar este arquivo.

1.  Crie um arquivo chamado `.env` na raiz do projeto.

2.  Adicione as seguintes chaves (substitua pelos seus valores):

    ```ini
    # Chave do Google AI Studio (para o Gemini)
    GOOGLE_API_KEY=SUA_CHAVE_GOOGLE_AI

    # Chave do Serper.dev (para busca de voos, hotéis e atividades)
    SERPER_API_KEY=SUA_CHAVE_SERPER
    ```

## ▶️ Como Executar

Após instalar as dependências e configurar o `.env`, inicie o agente principal:

```bash
python main.py
```

O console mostrará um prompt. Interaja com o agente em linguagem natural:

```
🌍 Bem-vindo ao Agente de Viagens Inteligente ✈️

Digite sua solicitação (ex: 'Planeje uma viagem de Curitiba a Paris de 10 a 15 de novembro com orçamento 400 reais e foco cultural')

Digite 'sair' para encerrar.

🧳 Você: [Sua solicitação aqui]
```