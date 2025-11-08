import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from tools import flights, hotels, activities, weather

# === CONFIGURAÇÃO ===
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY não definido no .env")
os.environ["GOOGLE_API_KEY"] = API_KEY

booking_integrator = Agent(
    name="travel_planner_agent",
    model="gemini-2.5-flash",
    description="Agente de viagens real que busca voos, hotéis, clima e atividades com APIs públicas.",
    tools=[
        flights.get_flight_options,
        hotels.get_hotel_options,
        activities.get_activities,
        weather.get_weather_forecast
    ],
)

# === LOOP PRINCIPAL ===
async def main():
    APP_NAME = "travel_planner_app"
    USER_ID = "user_1"
    SESSION_ID = "session_1"

    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    runner = Runner(agent=booking_integrator, app_name=APP_NAME, session_service=session_service)

    print("🌍 Bem-vindo ao Agente de Viagens Inteligente ✈️\n")
    print("Digite sua solicitação (ex: 'Planeje uma viagem de Curitiba a Paris de 10 a 15 de novembro com orçamento 400 reais e foco cultural')\n")
    print("Digite 'sair' para encerrar.\n")

    while True:
        user_prompt = input("🧳 Você: ").strip()
        if user_prompt.lower() in ["sair", "exit", "quit"]:
            print("👋 Encerrando sessão. Boa viagem!")
            await runner.close()
            break

        content = types.Content(role="user", parts=[types.Part(text=user_prompt)])
        print("\n🤖 Agente está processando...\n")

        # Executa o agente
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        ):
            # Funções chamadas pelo modelo
            function_calls = getattr(event, "function_calls", None)
            if function_calls:
                for call in function_calls:
                    print(f"🧩 [DEBUG] Chamando ferramenta: {call.name}({call.args})")

            # Texto retornado pelo modelo
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"📋 {part.text}")

if __name__ == "__main__":
    asyncio.run(main())
