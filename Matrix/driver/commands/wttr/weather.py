import requests
from Matrix.driver.commands.wttr.constants import WWO_CODE, WTTR_BASE


def getWeatherSimple():
    url:str = f"{WTTR_BASE}?M&format=j1"
    try:
        response: requests.Response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Unable to get weather info from {WTTR_BASE}, {e}")
    return None


def getTodayWeather():
    weather = getWeatherSimple()
    result = {}
    if weather is not None:
        weather = weather["current_condition"][0]

        result["tempFeelsLike"] = f'{weather["FeelsLikeC"]} °C'
        result["temp"] = f'{weather["temp_C"]} °C'
        result["tempFull"] = f'{weather["temp_C"]}°C ({weather["FeelsLikeC"]}°C)'
        result["weatherCode"] = f'{weather["weatherCode"]}'
        result["weatherLabel"] = f'{WWO_CODE[weather["weatherCode"]]}'
        result["windspeed"] = f'{weather["windspeedKmph"]}'

    return result
