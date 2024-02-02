import requests
from Matrix.driver.commands.wttr.constants import WWO_CODE, WTTR_BASE


def getWeatherSimple():

    url = f"{WTTR_BASE}?M&format=j1" 
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return None
  
def getTodayWeather():

    weather = getWeatherSimple()
    result = {}
    if weather:
        weather = weather["current_condition"][0]
        
        result["tempFeelsLike"] = f'{weather["FeelsLikeC"]} °C'
        result["temp"] = f'{weather["temp_C"]} °C'
        result["tempFull"] = f'{weather["temp_C"]}°C ({weather["FeelsLikeC"]}°C)'
        result["weatherCode"] = f'{weather["weatherCode"]}'
        result["weatherLabel"] = f'{WWO_CODE[weather["weatherCode"]]}'
        result["windspeed"] = f'{weather["windspeedKmph"]}'
        
    return result

