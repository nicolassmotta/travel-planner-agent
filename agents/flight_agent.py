import requests
import random
import os  # Importa a biblioteca 'os' para ler variáveis de ambiente

class FlightAgent:
    def __init__(self, environment):
        self.env = environment
        # Carrega a chave do ambiente (que o main.py populou)
        self.API_KEY = os.getenv("API_KEY_AVIATIONSTACK")
        
        # Esta verificação é o que disparou o erro
        if not self.API_KEY:
            raise ValueError("API_KEY_AVIATIONSTACK não encontrada. Verifique seu .env")
            
        self.API_URL = "http://api.aviationstack.com/v1/flights"

    def run(self, origem, destino, data):
        print(f"\n[Agente de Voos] Buscando voos reais de {origem} para {destino} (Usando Aviationstack)...")

        params = {
            'access_key': self.API_KEY,
            'dep_iata': origem,
            'arr_iata': destino,
            'flight_date': data,
            'limit': 10
        }

        voos_encontrados = []
        try:
            response = requests.get(self.API_URL, params=params)

            if response.status_code == 200:
                results = response.json().get('data', [])
                
                if not results:
                    print("  - Nenhum voo encontrado para essa rota/data.")
                    self.env.update("flights", [])
                    return

                for flight in results:
                    companhia = flight.get('airline', {}).get('name', 'Companhia Desconhecida')
                    horario_data = flight.get('departure', {}).get('scheduled', 'N/E')
                    horario = horario_data.split('T')[1][:5] if 'T' in horario_data else horario_data
                    preco_simulado = random.randint(800, 2500)

                    voos_encontrados.append({
                        "companhia": companhia,
                        "preco": preco_simulado,
                        "horario": horario
                    })

                melhores_voos = sorted(voos_encontrados, key=lambda v: v["preco"])[:2]
                self.env.update("flights", melhores_voos)
                print(f"Voos (reais) encontrados de {origem} para {destino} em {data}:")
                for voo in melhores_voos:
                    print(f"  - {voo['companhia']} | R${voo['preco']} (preço simulado) | {voo['horario']}")
            else:
                error_info = response.json().get('error', {})
                print(f"Erro na API do Aviationstack: {error_info.get('message', 'Erro desconhecido')}")
                self.env.update("flights", [])

        except Exception as e:
            print(f"Erro ao processar busca de voos: {e}")
            self.env.update("flights", [])