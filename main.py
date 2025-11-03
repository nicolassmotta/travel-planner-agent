from agents.flight_agent import FlightAgent
from agents.hotel_agent import HotelAgent
from agents.activities_agent import ActivitiesAgent
from agents.integration_agent import IntegrationAgent
from environment import TravelEnvironment

def main():
    print("=== SISTEMA DE RESERVA DE VIAGENS INTELIGENTE ===\n")

    origem = input("Digite a cidade de origem: ")
    destino = input("Digite a cidade de destino: ")
    data = input("Digite a data da viagem (YYYY-MM-DD): ")
    orcamento = float(input("Digite o orçamento total disponível (em R$): "))
    perfil = input("Digite o perfil do viajante (romântico, aventura, cultural, etc): ")

    # Cria o ambiente compartilhado
    env = TravelEnvironment()

    # Cria os agentes
    flight_agent = FlightAgent(env)
    hotel_agent = HotelAgent(env)
    activities_agent = ActivitiesAgent(env)
    integration_agent = IntegrationAgent(env)

    # Executa os agentes
    flight_agent.run(origem, destino, data)
    hotel_agent.run(destino, orcamento)
    activities_agent.run(destino, perfil)
    integration_agent.run()

    print("\n=== VIAGEM PLANEJADA COM SUCESSO ===")

if __name__ == "__main__":
    main()
