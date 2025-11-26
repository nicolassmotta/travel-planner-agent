# tools/recommendations.py
import os
import serpapi
import urllib.parse
from typing import Optional

def get_recommendations(city: str, category: str) -> str:
    """
    Busca recomendações e gera um link direto para o Google Maps.
    """
    
    print(f"🗺️ [LOG] Buscando recomendações '{category}' em {city}...")

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY não configurada no .env")

    # --- MELHORIA 2: Link direto para o Google Maps ---
    # Cria uma URL de busca no Maps (ex: "atrações turísticas em Paris")
    query_maps = f"top attractions in {city} {category}"
    encoded_query = urllib.parse.quote(query_maps)
    google_maps_url = f"https://www.google.com/maps/search/{encoded_query}?hl=pt-BR"

    # Busca na API (mantém a lógica original de busca web/places para texto)
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
        
        # Adiciona o link do Maps no final da resposta
        result += f"\n🔗 **[Explorar Atrações no Mapa (Google Maps)]({google_maps_url})**"
            
        return result
    except Exception as e:
        if isinstance(e, ValueError):
             raise e
        print(f"❌ Erro na API de recomendações: {e}")
        # Fallback robusto com o link do Maps
        return f"Não foi possível carregar detalhes textuais, mas você pode explorar o mapa:\n🔗 [Ver Atrações no Google Maps]({google_maps_url})"