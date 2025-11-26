# tools/weather.py
import requests
import urllib.parse
from datetime import datetime
from typing import Optional

def _get_coordinates(city: str):
    """Função auxiliar para obter coordenadas."""
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=pt&format=json"
    try:
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status() # Verifica erros HTTP
        geo_data = geo_response.json()
        if "results" not in geo_data or not geo_data["results"]:
            raise Exception(f"Não foi possível encontrar a cidade '{city}' no mapa.")
        
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        return lat, lon
    except Exception as e:
        # Erro na geocodificação deve parar a função
        raise Exception(f"Erro ao obter coordenadas para '{city}': {e}")


def _get_precipitation_summary(avg_precip: float) -> str:
    """Converte a média de mm de chuva em uma descrição amigável."""
    if avg_precip < 1.0:
        return f"Muito baixa ({avg_precip:.1f}mm/dia). O tempo deve ficar seco."
    elif avg_precip < 3.0:
        return f"Baixa ({avg_precip:.1f}mm/dia). Pode haver pancadas de chuva leves e ocasionais."
    elif avg_precip < 6.0:
        return f"Moderada ({avg_precip:.1f}mm/dia). É uma boa ideia levar um guarda-chuva."
    else:
        return f"Alta ({avg_precip:.1f}mm/dia). Prepare-se para alguns dias chuvosos."


def get_historical_average_weather(city: str, start_date: str, end_date: str) -> str:
    """
    Busca a MÉDIA HISTÓRICA do clima para um período e fornece link para previsão atual.
    """

    print(f"🌦️ [LOG] Buscando MÉDIA HISTÓRICA do clima para {city} entre {start_date} e {end_date}...")

    # --- MELHORIA 3: Link para Previsão em Tempo Real ---
    query_weather = f"weather in {city}"
    encoded_query = urllib.parse.quote(query_weather)
    google_weather_url = f"https://www.google.com/search?q={encoded_query}&hl=pt-BR"

    try:
        lat, lon = _get_coordinates(city)

        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        start_month_day = start_date_obj.strftime("%m-%d")
        end_month_day = end_date_obj.strftime("%m-%d")
        
        # Usar um ano bissexto (como 2024) para os dados de arquivo evita erros em 29/02
        api_start = f"2024-{start_month_day}"
        api_end = f"2024-{end_month_day}"

        weather_url = (
            f"https://archive-api.open-meteo.com/v1/era5?"
            f"latitude={lat}&longitude={lon}"
            f"&start_date={api_start}&end_date={api_end}"
            f"&daily=temperature_2m_mean,precipitation_sum"
            f"&timezone=auto"
        )
        
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status() # Verifica erros HTTP
        weather_data = weather_response.json()

        if "daily" not in weather_data:
             raise Exception(f"Não foi possível obter dados históricos para {city}.")

        avg_temp = sum(weather_data["daily"]["temperature_2m_mean"]) / len(weather_data["daily"]["temperature_2m_mean"])
        avg_precip = sum(weather_data["daily"]["precipitation_sum"]) / len(weather_data["daily"]["precipitation_sum"])

        precipitation_summary = _get_precipitation_summary(avg_precip)

        return (f"Clima Histórico Médio para {city} (Período de {start_month_day} a {end_month_day}):\n"
                f"* 🌡️ Temperatura média: {avg_temp:.1f}°C\n"
                f"* ☔ Chance de Chuva: {precipitation_summary}\n"
                f"(Baseado em dados climáticos de anos anteriores.)\n\n"
                f"🔗 **[Ver Previsão do Tempo em Tempo Real no Google]({google_weather_url})**")

    except Exception as e:
        print(f"[ERRO] Falha ao obter clima histórico: {e}")
        # Fallback: retorna pelo menos o link se a API falhar
        return (f"Não foi possível obter a média histórica do clima.\n"
                f"🔗 **[Verifique a Previsão Atual no Google]({google_weather_url})**")