import os
from google.adk import agents
from google.adk.sessions import InMemorySessionService
from app.tools import flights, hotels, recommendations, weather, images

# Configuração do Modelo (conforme seu agent.yaml)
MODEL_NAME = "gemini-2.5-flash"

# Lista de ferramentas importadas da pasta tools
tools_list = [
    flights.get_flight_options,
    hotels.get_hotel_options,
    recommendations.get_recommendations,
    weather.get_historical_average_weather,
    images.get_destination_images
]

# Inicializa o Agente com as instruções e ferramentas
booking_integrator = agents.Agent(
    name="travel_planner",
    model=MODEL_NAME,
    tools=tools_list,
    instruction="""
    Você é um agente planejador de viagens experiente. 
    Sua meta é criar roteiros detalhados e personalizados com base nas preferências do usuário.
    Use as ferramentas disponíveis para buscar voos, hotéis, previsões do tempo e imagens.
    Sempre verifique a previsão do tempo para sugerir atividades adequadas.
    Ao final, forneça um resumo financeiro estimado.
    """
)

# Inicializa o serviço de sessão (InMemory para desenvolvimento local)
# Isso permite que o 'runner' no plan.py mantenha o contexto da conversa
session_service = InMemorySessionService()