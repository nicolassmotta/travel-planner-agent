# tools/flights.py
import os
import serpapi # <-- 1. Importe apenas a biblioteca principal
from typing import Optional

def get_flight_options(origin: str, destination: str, date: str, return_date: Optional[str] = None) -> str:
    """
    Busca voos reais via SerpApi (usando a nova sintaxe do cliente).
    Usa a busca genérica "google" que aceita nomes de cidades.
    """
    
    log_message = f"🛫 [LOG] Buscando voos (SerpApi) de {origin} para {destination} (Ida: {date}"
    if return_date:
        log_message += f", Volta: {return_date}"
    log_message += ")..."
    print(log_message)

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "ERRO: SERPAPI_API_KEY não configurada no .env"

    # --- Query de busca genérica ---
    query = f"Google Flights voos de {origin} para {destination} em {date}"
    if return_date:
        query += f" volta {return_date}"
    
    # --- 2. Parâmetros para a nova biblioteca ---
    params = {
        "api_key": api_key,
        "engine": "google",
        "q": query,
        "gl": "br",
        "hl": "pt"
    }

    try:
        # --- 3. Nova sintaxe de busca ---
        client = serpapi.Client()
        results = client.search(params)
        
        # O resultado já é um dicionário
        organic_results = results.get("organic_results", [])

        if not organic_results:
            return f"Nenhum resultado encontrado para voos de {origin} para {destination}."

        result = f"Voos de {origin} para {destination} (Ida: {date}"
        if return_date:
            result += f", Volta: {return_date}"
        result += "):\n"

        for item in organic_results[:5]:
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            
            result += f"- {title}\n"
            if snippet:
                result += f"  '{snippet}'\n"
            result += f"  🔗 {link}\n"
            
        return result
    except Exception as e:
        return f"Erro ao buscar voos com SerpApi: {str(e)}"