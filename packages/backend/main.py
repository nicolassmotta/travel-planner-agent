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
from typing import Optional, AsyncGenerator

# Importações do FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from fastapi.responses import StreamingResponse

# === CONFIGURAÇÃO INICIAL ===
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY não definido no .env")
os.environ["GOOGLE_API_KEY"] = API_KEY

today_str = datetime.now().strftime("%Y-%m-%d")

# === INSTRUÇÕES DO AGENTE ===
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

# Modelo de dados Pydantic
class TravelRequest(BaseModel):
    origin: str
    destination: str
    departureDate: str
    returnDate: Optional[str] = None
    totalBudget: float
    nightlyBudget: float
    preferences: str

    @field_validator('totalBudget', 'nightlyBudget')
    def budgets_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('O orçamento não pode ser negativo')
        return v


async def stream_plan_response(request: TravelRequest) -> AsyncGenerator[str, None]:
    APP_NAME = "travel_planner"
    USER_ID = "user_api" 
    SESSION_ID = f"session_{datetime.now().timestamp()}" 

    print("\n--- NOVA REQUISIÇÃO (STREAM) RECEBIDA ---")
    print(f"Dados Recebidos: {request.model_dump_json(indent=2)}")

    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    runner = Runner(agent=booking_integrator, app_name=APP_NAME, session_service=session_service)

    final_return_date = request.returnDate
    if not final_return_date:
        final_return_date = request.departureDate

    user_prompt = f"""
    Planeje minha viagem com os seguintes detalhes:
    - Origem: {request.origin}
    - Destino: {request.destination}
    - Data de Ida: {request.departureDate}
    - Data de Volta: {final_return_date} 
    - Orçamento Total: R$ {request.totalBudget} 
    - Orçamento Hotel (por noite): R$ {request.nightlyBudget}
    - Preferências: {request.preferences}
    """

    print("\n--- PROMPT ENVIADO AO AGENTE ---")
    print(user_prompt)

    content = types.Content(role="user", parts=[types.Part(text=user_prompt)])
    
    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        ):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"--- STREAMING CHUNK: {part.text} ---")
                        yield part.text
    
    except Exception as e:
        print(f"!!!!!!!!!! ERRO NO AGENTE !!!!!!!!!!")
        print(f"Erro ao processar agente: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        yield f"\n\nERRO INTERNO DO SERVIDOR: {e}"
    finally:
        await runner.close()
        print("--- STREAM CONCLUÍDA ---")


# Endpoint principal da API
@app.post("/generate-plan")
async def generate_plan(request: TravelRequest):
    return StreamingResponse(stream_plan_response(request), media_type="text/event-stream")

# --- Para rodar o servidor ---
# Use o comando: uvicorn main:app --host 0.0.0.0 --port 8000 --reload