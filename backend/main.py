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
from pydantic import BaseModel

# === CONFIGURAÇÃO INICIAL ===
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY não definido no .env")
os.environ["GOOGLE_API_KEY"] = API_KEY

today_str = datetime.now().strftime("%Y-%m-%d")

# === INSTRUÇÕES DO AGENTE (Sem alteração) ===
agent_instructions = f"""
Você é um Coordenador de Viagens de elite. A data de HOJE é: {today_str}.

Sua tarefa é planejar a viagem passo a passo. 
NÃO chame todas as ferramentas de uma vez. Seja metódico:

1.  **VOOS:** Primeiro, sempre busque os voos usando 'get_flight_options'. Mostre os resultados ao usuário.
2.  **ORÇAMENTO:** Depois dos voos, verifique o orçamento. A ferramenta 'get_hotel_options' precisa de um orçamento "POR NOITE".
    -   Se o usuário der um orçamento TOTAL (ex: "R$20000 no total"), você DEVE PERGUNTAR: "Para a hospedagem, qual o valor máximo que você gostaria de gastar por noite?"
    -   NÃO tente calcular a diária sozinho. Pergunte ao usuário.
3.  **HOTÉIS:** Somente após saber o valor POR NOITE, chame 'get_hotel_options'.
4.  **ATIVIDADES:** Depois dos hotéis, pergunte o tipo de roteiro (ex: cultural, gastronômico) e chame 'get_recommendations'.
5.  **CLIMA:** Por fim, chame 'get_historical_average_weather' para o período.

Seja um coordenador: pergunte, execute UMA ferramenta, mostre o resultado, e então pergunte o próximo passo.
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

# Configuração do CORS para permitir requisições do seu frontend (Vite na porta 8080)
#
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

# Modelo de dados Pydantic para o request do frontend
# Deve bater com o schema do Zod do seu TravelForm.tsx
class TravelRequest(BaseModel):
    origin: str
    destination: str
    departureDate: str
    returnDate: Optional[str] = None
    totalBudget: str
    nightlyBudget: str
    preferences: str

# Endpoint principal da API
@app.post("/generate-plan")
async def generate_plan(request: TravelRequest):
    APP_NAME = "travel_planner"
    USER_ID = "user_api" # ID de usuário estático para a API
    SESSION_ID = f"session_{datetime.now().timestamp()}" # Nova sessão a cada request

    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    runner = Runner(agent=booking_integrator, app_name=APP_NAME, session_service=session_service)

    # Constrói o prompt inicial com todos os dados do formulário
    user_prompt = f"""
    Planeje minha viagem com os seguintes detalhes:
    - Origem: {request.origin}
    - Destino: {request.destination}
    - Data de Ida: {request.departureDate}
    - Data de Volta: {request.returnDate or 'Não definida'}
    - Orçamento Total: R$ {request.totalBudget}
    - Orçamento Hotel (por noite): R$ {request.nightlyBudget}
    - Preferências: {request.preferences}
    """

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
        print(f"Erro ao processar agente: {e}")
        return {"error": str(e)}, 500
    finally:
        await runner.close()

    # Retorna o plano completo como uma string única
    return {"plan": "\n".join(full_response)}

# --- Para rodar o servidor ---
# Use o comando: uvicorn main:app --host 0.0.0.0 --port 8000 --reload