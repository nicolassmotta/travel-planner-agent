# tools/recommendations.py
import os
import serpapi
from typing import Optional

def get_recommendations(city: str, category: str) -> str:
    """
    Busca recomendações, roteiros e dicas de viagem (ex: 'melhores
    restaurantes', 'roteiro cultural') usando a busca genérica do SerpApi.
    """
    
    print(f"🗺️ [LOG] Buscando recomendações '{category}' em {city}...")

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY não configurada no .env")

    query = f"roteiro de viagem {category} em {city} dicas"
    
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
            raise Exception(f"Nenhuma recomendação encontrada para '{query}'.")

        result = f"Recomendações e Roteiros para {category} em {city}:\n"

        for item in organic_results[:4]: # Pega os 4 primeiros
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
        print(f"❌ Erro na API de recomendações: {e}")
        raise Exception(f"Erro ao buscar recomendações: {str(e)}")