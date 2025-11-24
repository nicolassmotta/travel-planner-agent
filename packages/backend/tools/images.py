# tools/images.py
import os
import serpapi
from functools import lru_cache

@lru_cache(maxsize=32)
def get_destination_images(query: str) -> str:
    """
    Busca URLs de imagens para um local turístico, hotel ou cidade usando o Google Images.
    Útil para ilustrar o plano de viagem.
    """
    print(f"🖼️ [LOG] Buscando imagens para: '{query}'...")
    
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        # Se não tiver chave, retorna vazio silenciosamente para não quebrar o agente
        print("⚠️ SERPAPI_API_KEY não encontrada ao buscar imagens.")
        return ""

    params = {
        "api_key": api_key,
        "engine": "google_images",
        "q": query,
        "num": 3, # Pega 3 imagens para ter opções
        "gl": "br",
        "hl": "pt"
    }

    try:
        client = serpapi.Client()
        results = client.search(params)
        images_results = results.get("images_results", [])
        
        if not images_results:
            return "Nenhuma imagem encontrada."

        # Extrai apenas as URLs originais
        urls = [img["original"] for img in images_results if "original" in img]
        
        if not urls:
            return "Nenhuma URL de imagem válida encontrada."

        # Retorna formatado para o LLM
        return f"Imagens encontradas para '{query}' (use estas URLs no Markdown): " + ", ".join(urls)

    except Exception as e:
        print(f"❌ Erro ao buscar imagens: {e}")
        return ""