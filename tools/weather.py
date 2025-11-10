# tools/weather.py
import requests
from datetime import datetime
from typing import Optional

# Função auxiliar para obter coordenadas (sem alteração)
def _get_coordinates(city: str):
    geo_url = f"https://geocoding-api.open-Meteo.com/v1/search?name={city}&count=1&language=pt&format=json"
    geo_response = requests.get(geo_url)
    geo_data = geo_response.json()
    if "results" not in geo_data or not geo_data["results"]:
        raise Exception(f"Não foi possível encontrar a cidade '{city}' no mapa.")
    
    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]
    return lat, lon

def get_historical_average_weather(city: str, start_date: str, end_date: str) -> str:
    """
    Busca a MÉDIA HISTÓRICA do clima para um período.
    Usa a API 'archive' da Open-Meteo, que analisa dados de anos passados.
    Ideal para planejamento de viagens futuras (ex: como é o clima em Nov/2025).
    """

    print(f"🌦️ [LOG] Buscando MÉDIA HISTÓRICA do clima para {city} entre {start_date} e {end_date}...")

    try:
        lat, lon = _get_coordinates(city)

        # Converte datas YYYY-MM-DD para o formato MM-DD
        # A API histórica não se importa com o ano para médias
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Formato da API histórica (ex: "11-20")
        start_month_day = start_date_obj.strftime("%m-%d")
        end_month_day = end_date_obj.strftime("%m-%d")
        
        # A API de média diária usa 'start_date' e 'end_date' com um ano fixo (ex: 2023)
        # para definir o período do ano.
        api_start = f"2023-{start_month_day}"
        api_end = f"2023-{end_month_day}"

        # URL da API de Clima Histórico (ERA5 - cobre de 1940 até hoje)
        weather_url = (
            f"https://archive-api.open-meteo.com/v1/era5?"
            f"latitude={lat}&longitude={lon}"
            f"&start_date={api_start}&end_date={api_end}"
            f"&daily=temperature_2m_mean,precipitation_sum"
            f"&timezone=auto"
        )
        
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        if "daily" not in weather_data:
             return f"Não foi possível obter dados históricos para {city}."

        # Pega a média dos valores diários
        avg_temp = sum(weather_data["daily"]["temperature_2m_mean"]) / len(weather_data["daily"]["temperature_2m_mean"])
        avg_precip = sum(weather_data["daily"]["precipitation_sum"]) / len(weather_data["daily"]["precipitation_sum"])

        return (f"Clima Histórico Médio para {city} (Período de {start_month_day} a {end_month_day}):\n"
                f"* 🌡️ Temperatura média: {avg_temp:.1f}°C\n"
                f"* ☔ Precipitação média: {avg_precip:.1f}mm por dia\n"
                f"(Baseado em dados climáticos de anos anteriores.)")

    except Exception as e:
        print(f"[ERRO] Falha ao obter clima histórico: {e}")
        return f"Não foi possível obter a média histórica do clima: {e}"