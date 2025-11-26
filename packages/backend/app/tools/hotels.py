# tools/hotels.py
import os
import serpapi
import urllib.parse
from typing import Optional

def get_hotel_options(city: str, check_in: str, check_out: str, budget: float) -> str:
    """
    Busca hotéis e gera um link direto para o Google Travel com a pesquisa preenchida.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    print(f"🏨 [LOG] Buscando hotéis em {city} ({check_in} a {check_out}) até R${budget}/noite...")

    if not api_key:
        raise ValueError("SERPAPI_API_KEY não configurada no .env")

    # 1. CONSTRUÇÃO DO LINK DIRETO (A Melhoria)
    # Construímos uma query em linguagem natural que o Google entende
    # Ex: "Hotels in Paris from 2023-10-10 to 2023-10-15 max price 500 BRL"
    query_text = f"Hotels in {city} from {check_in} to {check_out}"
    if budget > 0:
        query_text += f" max price {int(budget)} BRL"
    
    encoded_query = urllib.parse.quote(query_text)
    
    # URL direta para a secção de hotéis
    google_hotels_url = f"https://www.google.com/travel/hotels?q={encoded_query}&hl=pt-BR&curr=BRL"

    # 2. BUSCA DE DADOS VIA API (Para o Agente ler e resumir)
    params = {
        "api_key": api_key,
        "engine": "google_hotels",
        "q": city,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "max_price": int(budget) if budget > 0 else None,
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
            print("🏨 [LOG] Motor 'google_hotels' não retornou resultados. Tentando fallback genérico...")
            return _search_hotels_fallback(city, budget, api_key, google_hotels_url)

        result = f"Opções de hotéis em {city} (até R${budget}/noite, ordenados por preço):\n"
        
        for item in properties[:5]:
            title = item.get("name", "")
            rate = item.get("rate_per_night", {})
            price = rate.get("lowest", item.get("price", "N/A"))
            rating = item.get("overall_rating", "N/A")
            gps = item.get("gps_coordinates", {})
            
            result += f"- {title}\n"
            result += f"  Preço: {price} | Avaliação: {rating} ★\n"
        
        # 3. ANEXAR O LINK NO FINAL
        result += f"\n🔗 **[Ver Hotéis e Reservar no Google Travel]({google_hotels_url})**"
        result += "\n(Link com datas e filtros de preço já aplicados)"
        
        return result
    
    except Exception as e:
        print(f"❌ Erro inesperado ao buscar hotéis: {e}")
        # Se a API falhar, o utilizador ainda recebe o link funcional
        return f"Não foi possível carregar a lista detalhada, mas você pode ver os hotéis disponíveis no link:\n🔗 [Ver Hotéis no Google]({google_hotels_url})"


def _search_hotels_fallback(city: str, budget: float, api_key: str, url: str) -> str:
    """
    Fallback usando busca genérica, mas retornando o link direto correto.
    """
    query_string = f"hotéis em {city} baratos"
    
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
        organic = results.get("organic_results", [])
        
        res = f"Sugestões de hotéis em {city} (via busca genérica):\n"
        for item in organic[:4]:
            res += f"- {item.get('title')}: {item.get('snippet')}\n"
            
        res += f"\n🔗 **[Ver Hotéis e Reservar no Google Travel]({url})**"
        return res
    except Exception as e:
        return f"Consulte os hotéis diretamente no link:\n🔗 [Ver Hotéis]({url})"