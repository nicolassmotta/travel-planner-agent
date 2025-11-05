from dotenv import load_dotenv

# Carrega as variáveis do .env ANTES de importar os agentes
load_dotenv()

# Agora o restante das importações
from agents.flight_agent import FlightAgent
from agents.hotel_agent import HotelAgent
from agents.activities_agent import ActivitiesAgent
from agents.integration_agent import IntegrationAgent
from environment import TravelEnvironment

def main():
    print("=== SISTEMA DE RESERVA DE VIAGENS INTELIGENTE ===\n")

    # --- INPUTS MELHORADOS ---
    origem_iata = input("Digite o CÓDIGO IATA de origem (ex: CWB, GRU): ").upper()
    destino_iata = input("Digite o CÓDIGO IATA de destino (ex: GIG, CDG): ").upper()
    
    # Input separado para os agentes que não usam IATA
    cidade_destino_nome = input(f"Digite o nome da cidade de destino (ex: Rio de Janeiro): ")
    
    data = input("Digite a data da viagem (YYYY-MM-DD): ")
    
    try:
        orcamento = float(input("Digite o orçamento total disponível (em R$): "))
    except ValueError:
        print("Orçamento inválido. Usando R$ 5000.00 como padrão.")
        orcamento = 5000.0
        
    perfil = input("Digite o perfil do viajante (romântico, aventura, cultural, etc): ")

    # Cria o ambiente compartilhado
    env = TravelEnvironment()

    try:
        # Cria os agentes
        # O erro acontecia aqui, pois load_dotenv() não tinha sido chamado
        flight_agent = FlightAgent(env)
        hotel_agent = HotelAgent(env)
        activities_agent = ActivitiesAgent(env)
        integration_agent = IntegrationAgent(env)

        # Executa os agentes com os parâmetros corretos
        flight_agent.run(origem_iata, destino_iata, data)
        hotel_agent.run(cidade_destino_nome, orcamento)
        activities_agent.run(cidade_destino_nome, perfil)
        integration_agent.run()

        print("\n=== VIAGEM PLANEJADA COM SUCESSO ===")

    except ValueError as e:
        # Esta é a mensagem de erro que você viu
        print(f"\nERRO CRÍTICO: {e}")
        print("Verifique se suas chaves de API estão corretas no arquivo .env")


if __name__ == "__main__":
    main()