import requests
from datetime import datetime, timedelta
from typing import Optional # <-- ADICIONE ESTA LINHA

def get_weather_forecast(city: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str: # <-- MUDE AQUI
    """
    Retorna a previsão do tempo para uma cidade usando a API gratuita do Open-Meteo.
    Se start_date e end_date (formato YYYY-MM-DD) forem fornecidos, busca para esse período.
    Caso contrário, busca para os próximos 3 dias (hoje + 2 dias).
    """

    print(f"🌤️ [LOG] Buscando previsão do tempo para {city}...")

    try:
        # 1️⃣ Obter coordenadas (lat/lon) da cidade
        geo_url = f"https://geocoding-api.open-Meteo.com/v1/search?name={city}&count=1&language=pt&format=json"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            return f"Não foi possível encontrar a cidade '{city}' no mapa."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # --- Lógica de Data Atualizada ---
        if start_date and end_date:
            print(f"🌤️ [LOG] Usando período customizado: {start_date} a {end_date}")
            start_date_api = start_date
            end_date_api = end_date
            # Limita a resposta a um máximo de 10 dias para não ficar muito longa
            limit_days = 10 
        else:
            print(f"🌤️ [LOG] Usando período padrão (próximos 3 dias)")
            today = datetime.now().date()
            start_date_api = today.strftime("%Y-%m-%d")
            # O período é inclusivo, então +2 dias = 3 dias no total (hoje, amanhã, depois)
            end_date_api = (today + timedelta(days=2)).strftime("%Y-%m-%d") 
            limit_days = 3
        # --- Fim da Lógica de Data ---


        # 3️⃣ Consultar previsão do tempo (agora com datas dinâmicas)
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&start_date={start_date_api}&end_date={end_date_api}" # Datas dinâmicas
            f"&timezone=auto"
        )

        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        daily = weather_data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precipitation = daily.get("precipitation_sum", [])

        if not dates:
            return f"Não foi possível obter dados de previsão para {city} no período de {start_date_api} a {end_date_api}."

        # 4️⃣ Montar resposta formatada
        forecast_lines = []
        # O loop agora usa o limite que definimos
        for i in range(min(limit_days, len(dates))):
            date = datetime.strptime(dates[i], "%Y-%m-%d").strftime("%d/%m/%Y")
            line = (
                f"* **{date}:** 🌡️ {min_temps[i]}°C a {max_temps[i]}°C"
                f", ☔ {precipitation[i]}mm de chuva"
            )
            forecast_lines.append(line)
        
        period_desc = f"Período de {datetime.strptime(start_date_api, '%Y-%m-%d').strftime('%d/%m')} a {datetime.strptime(end_date_api, '%Y-%m-%d').strftime('%d/%m')}"
        if limit_days == 3 and not (start_date and end_date):
             period_desc = "Próximos 3 dias"

        return f"Previsão ({period_desc}):\n" + "\n".join(forecast_lines)

    except Exception as e:
        print(f"[ERRO] Falha ao obter previsão do tempo: {e}")
        return "Não foi possível obter a previsão do tempo no momento."