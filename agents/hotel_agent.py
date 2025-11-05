import requests
import json 
import os  # Importa a biblioteca 'os'

class HotelAgent:
    def __init__(self, environment):
        self.env = environment
        # Carrega a chave do ambiente
        self.API_KEY = os.getenv("API_KEY_GOOGLE")
        
        if not self.API_KEY:
            raise ValueError("API_KEY_GOOGLE não encontrada. Verifique seu .env")

    def run(self, cidade, orcamento):
        print(f"\n[Agente de Hospedagem] Buscando hotéis reais em {cidade} (Usando API Nova)...")

        url = "https://places.googleapis.com/v1/places:searchText"
        
        payload = {
            "textQuery": f"hoteis em {cidade}",
            "languageCode": "pt-BR"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.API_KEY,  # A chave é usada aqui
            "X-Goog-FieldMask": "places.displayName,places.rating,places.formattedAddress"
        }

        hoteis_reais = []
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                results = response.json().get('places', [])
                
                for place in results:
                    hoteis_reais.append({
                        "nome": place.get('displayName', {}).get('text', 'Nome não encontrado'),
                        "preco_noite": 0, # <-- Lembrete: API do Places não dá preço
                        "avaliacao": place.get('rating', 0.0),
                        "endereco": place.get('formattedAddress')
                    })
                
                viaveis = sorted(hoteis_reais, key=lambda h: h['avaliacao'], reverse=True)
                self.env.update("hotels", viaveis)

                print(f"Hotéis reais encontrados em {cidade} (ordenados por avaliação):")
                if not viaveis:
                    print("  - Nenhum hotel encontrado.")
                for hotel in viaveis:
                    print(f"  - {hotel['nome']} | Avaliação: {hotel['avaliacao']}")
            
            else:
                error = response.json().get('error', {})
                print(f"Erro na API do Google: {error.get('message', 'Erro desconhecido')}")
                self.env.update("hotels", [])

        except Exception as e:
            print(f"Erro ao buscar hotéis: {e}")
            self.env.update("hotels", [])