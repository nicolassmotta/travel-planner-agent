# tools/hotels.py
import os
import serpapi
from typing import Optional

def get_hotel_options(city: str, check_in: str, check_out: str, budget: float) -> str:
    """
    Busca hotéis reais via SerpApi (usando a nova sintaxe do cliente).
    Usa 'engine: google_hotels' e o parâmetro 'max_price'.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    print(f"🏨 [LOG] Buscando hotéis (SerpApi) em {city} ({check_in} a {check_out}) até R${budget}/noite...")

    if not api_key:
        raise ValueError("SERPAPI_API_KEY não configurada no .env")

    params = {
        "api_key": api_key,
        "engine": "google_hotels",
        "q": city,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "max_price": int(budget),
        "currency": "BRL",
        "gl": "br",
        "hl": "pt",
        "sort_by": "3" # 3 = 'Lowest price'
    }

    try:
        client = serpapi.Client()
        results = client.search(params)
        
        properties = results.get("properties")

        if not properties:
            print("🏨 [LOG] Motor 'google_hotels' não retornou. Tentando busca genérica...")
            return _search_hotels_generic(city, check_in, check_out, budget, api_key)

        result = f"Opções de hotéis em {city} (até R${budget}/noite, ordenados por preço):\n"
        
        for item in properties[:5]:
            title = item.get("name", "")
            rate = item.get("rate_per_night", {})
            price = rate.get("lowest")
            
            if not price:
                 price = item.get("price", "N/A")

            rating = item.get("overall_rating", "N/A")
            link = item.get("link", "")
            
            result += f"- {title}\n"
            result += f"  Preço: {price} | Avaliação: {rating} ★\n"
            if link:
                result += f"  🔗 Link: {link}\n"
        
        return result
    
    except Exception as e:
        if isinstance(e, ValueError):
             raise e
        print(f"❌ Erro inesperado ao buscar hotéis: {e}")
        # Tenta a busca genérica como último recurso
        try:
            return _search_hotels_generic(city, check_in, check_out, budget, api_key)
        except Exception as generic_e:
            # Se a busca genérica também falhar, levanta o erro
            print(f"❌ Erro na busca genérica de fallback: {generic_e}")
            raise Exception(f"Erro ao buscar hotéis (falha na API primária e no fallback): {generic_e}")


def _search_hotels_generic(city: str, check_in: str, check_out: str, budget: float, api_key: str) -> str:
    """Função de fallback para busca genérica de hotéis."""
    
    query_string = f"hotéis em {city} de {check_in} até {check_out} por até R${budget} por noite (site:booking.com OR site:decolar.com)"
    
    params = {
        "api_key": api_key,
        "engine": "google",
        "q": query_string,
        "gl": "br",
        "hl": "pt"
    }

    try:
        client = serpapi.Client()
        results = client.search(params)
        
        organic_results = results.get("organic_results", [])
        
        if not organic_results:
             raise Exception(f"Nenhum hotel encontrado para {city} com esses filtros (fallback).")

        result = f"Opções de hotéis em {city} (busca genérica):\n"
        for item in organic_results[:5]:
            title = item.get("title", "")
            link = item.get("link", "")
            result += f"- {title}\n  🔗 {link}\n"
        return result
    except Exception as e:
        if isinstance(e, ValueError):
             raise e
        raise Exception(f"Erro na busca genérica de hotéis: {e}")