# main.py
import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
# Verifique se 'recommendations' está aqui
from tools import flights, hotels, recommendations, weather 
from datetime import datetime

# === CONFIGURAÇÃO ===
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY não definido no .env")
os.environ["GOOGLE_API_KEY"] = API_KEY

today_str = datetime.now().strftime("%Y-%m-%d")

# === INSTRUÇÕES DE COORDENADOR (A MUDANÇA PRINCIPAL) ===
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

# Voltamos ao agente único (monolítico), mas com cérebro de coordenador
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

# === LOOP PRINCIPAL (Sem alteração) ===
async def main():
    APP_NAME = "travel_planner"
    USER_ID = "user_1"
    SESSION_ID = "session_1"

    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    # O Runner executa o agente único
    runner = Runner(agent=booking_integrator, app_name=APP_NAME, session_service=session_service)

    print("🌍 Bem-vindo ao Agente de Viagens Inteligente (Versão Coordenador) ✈️\n")
    print(f"(Contexto do Agente: Hoje é {today_str})\n")
    print("Digite sua solicitação (ex: 'Planeje uma viagem de São Paulo para Roma de 20/11 a 30/11/2025 com orçamento total de 20000 reais e foco cultural')\n")
    print("Digite 'sair' para encerrar.\n")

    while True:
        user_prompt = input("🧳 Você: ").strip()
        if user_prompt.lower() in ["sair", "exit", "quit"]:
            print("👋 Encerrando sessão. Boa viagem!")
            await runner.close()
            break

        content = types.Content(role="user", parts=[types.Part(text=user_prompt)])
        print("\n🤖 Agente está processando...\n")

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        ):
            function_calls = getattr(event, "function_calls", None)
            if function_calls:
                for call in function_calls:
                    print(f"🧩 [DEBUG] Chamando ferramenta: {call.name}({call.args})")

            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"📋 {part.text}")

if __name__ == "__main__":
    asyncio.run(main())