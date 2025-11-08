import os
import requests
from typing import Optional

def get_hotel_options(city: str, check_in: str, check_out: str, budget: float) -> str:
    """
    Busca hotéis reais via Google Search (Serper.dev API).
    Usa a mesma API SERPER_API_KEY dos módulos de voos e atividades.
    """
    api_key = os.getenv("SERPER_API_KEY")
    print(f"🏨 [LOG] Buscando hotéis em {city} ({check_in} a {check_out}) até R${budget}/noite... (via Serper)")

    # === Verificação da Chave ===
    if not api_key:
        print("❌ [ERRO] SERPER_API_KEY ausente — A busca de hotéis não funcionará.")
        return "ERRO: A chave SERPER_API_KEY (usada para voos/atividades) não está configurada no .env."

    # === API real (Serper) ===
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    # --- CORREÇÃO AQUI: Agrupando os sites com parênteses ---
    query_string = f"hotéis em {city} de {check_in} até {check_out} por até R${budget} por noite (site:booking.com OR site:decolar.com OR site:hoteis.com)"
    
    payload = {
        "q": query_string
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status() # Lança erro para 4xx/5xx
        data = response.json()

        if not data.get("organic"):
            return f"Nenhum resultado encontrado para hotéis em {city} com esses filtros."

        result = f"Opções de hotéis em {city} (até R${budget}/noite):\n"
        # Pega os 5 primeiros resultados
        for item in data["organic"][:5]:
            title = item.get("title", "")
            link = item.get("link", "")
            result += f"- {title}\n  🔗 {link}\n"
        
        return result
    
    except requests.exceptions.HTTPError as http_err:
        print(f"❌ Erro HTTP na API Serper (Hotéis): {http_err}")
        return f"Erro ao contatar a API de busca de hotéis (HTTP {http_err.response.status_code})."
    except Exception as e:
        print(f"❌ Erro inesperado ao buscar hotéis: {e}")
        return f"Ocorreu um erro ao buscar hotéis: {e}"