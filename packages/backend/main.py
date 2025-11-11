# main.py
import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from tools import flights, hotels, recommendations, weather
from datetime import datetime
from typing import Optional

# Importações do FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# === CONFIGURAÇÃO INICIAL ===
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY não definido no .env")
os.environ["GOOGLE_API_KEY"] = API_KEY

today_str = datetime.now().strftime("%Y-%m-%d")

# === INSTRUÇÕES DO AGENTE (Mesma da última vez) ===
agent_instructions = f"""
Você é um Coordenador de Viagens de elite. A data de HOJE é: {today_str}.

Sua tarefa é gerar um plano de viagem completo e detalhado em UMA ÚNICA RESPOSTA.
Você receberá todos os dados do usuário de uma vez (origem, destino, datas, orçamentos, preferências).
Você NÃO PODE fazer perguntas de volta. O usuário não pode respondê-lo.

Use as ferramentas fornecidas na seguinte ordem para construir o plano:

1.  **VOOS:** Chame 'get_flight_options' com a origem, destino e datas fornecidas.
2.  **HOTÉIS:** Chame 'get_hotel_options'. A ferramenta retornará nomes, preços, avaliações e, se possível, links. Inclua todos esses dados.
3.  **ATIVIDADES:** Chame 'get_recommendations' com o destino e use as 'preferences' do usuário como a 'category' da busca.
4.  **CLIMA:** Chame 'get_historical_average_weather'. A ferramenta retornará a temperatura média e uma **descrição sobre a chance de chuva**. Inclua essa descrição no relatório.

Ao final, compile TODAS as informações (voos, hotéis, atividades e clima) em um relatório único e formatado em markdown para o usuário.
Seja claro e organizado.
"""

# === INICIALIZAÇÃO DO AGENTE E SERVIÇOS ===
booking_integrator = LlmAgent(
    name="travel_planner",
    model="gemini-2.5-flash",
    description="Agente de viagens que coordena o planejamento passo a passo.",
    instruction=agent_instructions,
    tools=[
        flights.get_flight_options,
        hotels.get_hotel_options,
        recommendations.get_recommendations,
        weather.get_historical_average_weather
    ],
)

session_service = InMemorySessionService()

# === DEFINIÇÃO DA API ===
app = FastAPI()

# Configuração do CORS (sem alteração)
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de dados Pydantic (CORRIGIDO)
# Voltamos a aceitar 'str' para os orçamentos, para não dar erro 422
class TravelRequest(BaseModel):
    origin: str
    destination: str
    departureDate: str
    returnDate: Optional[str] = None
    totalBudget: str  # <--- CORREÇÃO AQUI
    nightlyBudget: str # <--- CORREÇÃO AQUI
    preferences: str

# Endpoint principal da API
@app.post("/generate-plan")
async def generate_plan(request: TravelRequest):
    APP_NAME = "travel_planner"
    USER_ID = "user_api" 
    SESSION_ID = f"session_{datetime.now().timestamp()}" 

    print("\n--- NOVA REQUISIÇÃO RECEBIDA ---")
    print(f"Dados Recebidos: {request.model_dump_json(indent=2)}")

    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    runner = Runner(agent=booking_integrator, app_name=APP_NAME, session_service=session_service)

    # --- INÍCIO DA CORREÇÃO ---
    # Validamos a data de volta AQUI, antes de enviar ao agente.
    final_return_date = request.returnDate
    if not final_return_date:
        final_return_date = request.departureDate

    # Convertemos os orçamentos de string para float AQUI.
    # Se a string estiver vazia ou for inválida, usamos 0.0
    try:
        total_budget_float = float(request.totalBudget)
    except (ValueError, TypeError):
        total_budget_float = 0.0

    try:
        nightly_budget_float = float(request.nightlyBudget)
    except (ValueError, TypeError):
        nightly_budget_float = 0.0
    # --- FIM DA CORREÇÃO ---


    # Constrói o prompt inicial com os dados do formulário JÁ VALIDADOS E CONVERTIDOS
    user_prompt = f"""
    Planeje minha viagem com os seguintes detalhes:
    - Origem: {request.origin}
    - Destino: {request.destination}
    - Data de Ida: {request.departureDate}
    - Data de Volta: {final_return_date} 
    - Orçamento Total: R$ {total_budget_float}
    - Orçamento Hotel (por noite): R$ {nightly_budget_float}
    - Preferências: {request.preferences}
    """

    print("\n--- PROMPT ENVIADO AO AGENTE ---")
    print(user_prompt)

    content = types.Content(role="user", parts=[types.Part(text=user_prompt)])
    
    full_response = []

    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        ):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        full_response.append(part.text)
    
    except Exception as e:
        print(f"!!!!!!!!!! ERRO NO AGENTE !!!!!!!!!!")
        print(f"Erro ao processar agente: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return {"error": f"Erro interno do agente: {e}"}
    finally:
        await runner.close()

    final_plan = "\n".join(full_response)
    print("\n--- RESPOSTA FINAL DO AGENTE ---")
    print(final_plan)
    print("----------------------------------\n")

    # Retorna o plano completo
    return {"plan": final_plan}

# --- Para rodar o servidor ---
# Use o comando: uvicorn main:app --host 0.0.0.0 --port 8000 --reload