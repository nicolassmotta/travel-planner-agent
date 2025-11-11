# tools/flights.py
import os
import serpapi
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
        raise ValueError("SERPAPI_API_KEY não configurada no .env")

    query = f"Google Flights voos de {origin} para {destination} em {date}"
    if return_date:
        query += f" volta {return_date}"
    
    params = {
        "api_key": api_key,
        "engine": "google",
        "q": query,
        "gl": "br",
        "hl": "pt"
    }

    try:
        client = serpapi.Client()
        results = client.search(params)
        
        organic_results = results.get("organic_results", [])

        if not organic_results:
            raise Exception(f"Nenhum resultado encontrado para voos de {origin} para {destination}.")

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
        if isinstance(e, ValueError):
             raise e
        print(f"❌ Erro na API de voos: {e}")
        raise Exception(f"Erro ao buscar voos com SerpApi: {str(e)}")