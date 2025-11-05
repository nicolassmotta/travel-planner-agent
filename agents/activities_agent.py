import requests
import json 
import os  # Importa a biblioteca 'os'

class ActivitiesAgent:
    def __init__(self, environment):
        self.env = environment
        # Carrega a chave do ambiente
        self.API_KEY = os.getenv("API_KEY_GOOGLE")
        
        if not self.API_KEY:
            raise ValueError("API_KEY_GOOGLE não encontrada. Verifique seu .env")

    def run(self, cidade, perfil):
        print(f"\n[Agente de Atividades] Recomendando atividades reais para '{perfil}' em {cidade} (Usando API Nova)...")

        url = "https://places.googleapis.com/v1/places:searchText"
        
        payload = {
            "textQuery": f"atividades {perfil} em {cidade}",
            "languageCode": "pt-BR"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.API_KEY,  # A chave é usada aqui
            "X-Goog-FieldMask": "places.displayName"
        }
        
        atividades_reais = []
        try:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                results = response.json().get('places', [])
                
                for place in results:
                    atividades_reais.append(place.get('displayName', {}).get('text', 'Atividade'))
                
                if not atividades_reais:
                    atividades_reais = ["Passeio pelo centro da cidade"]

                self.env.update("activities", atividades_reais)
                print(f"Atividades reais sugeridas para perfil '{perfil}' em {cidade}:")
                for a in atividades_reais:
                    print(f"  - {a}")
            
            else:
                 error = response.json().get('error', {})
                 print(f"Erro na API do Google: {error.get('message', 'Erro desconhecido')}")
                 self.env.update("activities", ["Passeio pela cidade (erro na busca)"])

        except Exception as e:
            print(f"Erro ao buscar atividades: {e}")
            self.env.update("activities", ["Passeio pela cidade (erro na busca)"])