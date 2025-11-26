# tools/flights.py
import os
import serpapi
import urllib.parse
from typing import Optional

def get_flight_options(origin: str, destination: str, date: str, return_date: Optional[str] = None) -> str:
    """
    Busca voos e gera um link direto para o Google Flights com a pesquisa preenchida.
    """
    
    print(f"🛫 [LOG] Buscando voos de {origin} para {destination}...")

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY não configurada no .env")

    # 1. CONSTRUÇÃO DO LINK DIRETO (Resolve o problema do site genérico)
    # O Google Flights aceita consultas em linguagem natural via parâmetro 'q'
    query_text = f"Flights from {origin} to {destination} on {date}"
    if return_date:
        query_text += f" returning {return_date}"
    
    # Codifica a string para formato de URL
    encoded_query = urllib.parse.quote(query_text)
    
    # Monta a URL final forçando moeda (BRL) e idioma (pt-BR)
    google_flights_url = f"https://www.google.com/travel/flights?q={encoded_query}&hl=pt-BR&curr=BRL"

    # 2. BUSCA DE DADOS (Para o Agente ler)
    # Usamos 'google_flights' engine se possível para dados estruturados, 
    # mas a busca 'google' genérica é mais tolerante com nomes de cidades vs códigos IATA.
    # Vamos manter a busca genérica para obter os snippets, mas anexar o link correto.
    
    params = {
        "api_key": api_key,
        "engine": "google",
        "q": f"Google Flights voos {origin} para {destination}",
        "gl": "br",
        "hl": "pt"
    }

    try:
        client = serpapi.Client()
        results = client.search(params)
        organic_results = results.get("organic_results", [])

        result_text = f"Opções de voos de {origin} para {destination} (Ida: {date}"
        if return_date:
            result_text += f", Volta: {return_date}"
        result_text += "):\n"

        # Adiciona algumas opções de texto para o Agente comentar
        if organic_results:
            for item in organic_results[:3]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                result_text += f"- {title}: {snippet}\n"
        else:
            result_text += "- Consulte o link abaixo para ver as opções em tempo real.\n"

        # 3. ANEXAR O LINK DIRETO NO RETORNO
        # Isso garante que o Agente inclua este link específico na resposta final markdown
        result_text += f"\n🔗 **[Ver Passagens e Preços no Google Voos]({google_flights_url})**"
        result_text += "\n(O link acima já abre com as datas e locais preenchidos)"
            
        return result_text

    except Exception as e:
        print(f"❌ Erro na API de voos: {e}")
        # Mesmo se a API falhar, retornamos o link construído manualmente, pois ele não depende da API
        return f"Não foi possível carregar os detalhes dos voos via API, mas você pode verificar diretamente no link:\n🔗 [Ver voos no Google Flights]({google_flights_url})" 