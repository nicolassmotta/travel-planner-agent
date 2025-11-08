import os
import requests
from typing import Optional

def get_flight_options(origin: str, destination: str, date: str, return_date: Optional[str] = None) -> str:
    """
    Busca voos reais via Google Search (Serper.dev API).
    Agora inclui uma data de volta opcional (formato YYYY-MM-DD).
    """
    
    # --- Lógica de Log Atualizada ---
    log_message = f"🛫 [LOG] Buscando voos reais de {origin} para {destination} (Ida: {date}"
    if return_date:
        log_message += f", Volta: {return_date}"
    log_message += ")..."
    print(log_message)

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }
    
    # --- Query de busca dinâmica ---
    query = f"voos de {origin} para {destination} em {date}"
    if return_date:
        query += f" volta {return_date}"
    
    # --- CORREÇÃO AQUI: Agrupando os sites com parênteses ---
    query += " (site:skyscanner.com OR site:decolar.com OR site:google.com/travel/flights)"
    
    payload = { "q": query }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        if not data.get("organic"):
            return f"Nenhum resultado encontrado para voos de {origin} para {destination}."

        # --- Resposta formatada dinâmica ---
        result = f"Voos de {origin} para {destination} (Ida: {date}"
        if return_date:
            result += f", Volta: {return_date}"
        result += "):\n"

        for item in data["organic"][:5]:
            title = item.get("title", "")
            link = item.get("link", "")
            result += f"- {title}\n  🔗 {link}\n"
        return result
    except Exception as e:
        return f"Erro ao buscar voos: {str(e)}"