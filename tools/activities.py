import os
import requests

def get_activities(city: str, category: str = "cultural") -> str:
    """
    Busca atividades reais via Google Search (Serper.dev)
    """
    print(f"🎭 [LOG] Buscando atividades {category} em {city}...")

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "q": f"principais atrações turísticas {category} em {city}"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        if not data.get("organic"):
            return f"Nenhuma atividade encontrada em {city}."

        result = f"Atividades {category} recomendadas em {city}:\n"
        for item in data["organic"][:5]:
            title = item.get("title", "")
            link = item.get("link", "")
            result += f"- {title}\n  🔗 {link}\n"
        return result
    except Exception as e:
        return f"Erro ao buscar atividades: {str(e)}"
