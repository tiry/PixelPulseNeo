import requests
from datetime import datetime, timedelta
import json
import xml.etree.ElementTree as ET

BASE_API_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

SINUS_HEIGHT:float = 40.0

def get_api_url(
    date:str = "today",
    product:str = "predictions",
    station:str = "8511907",
    format:str = "json",
    application:str = "LED_Matrix",
    units:str = "english",
    time_zone:str = "lst_ldt",
    datum:str = "MLLW",
    interval:str|None=None
) -> str:
    """
    https://tidesandcurrents.noaa.gov/api/
    """
    url: str =  f"{BASE_API_URL}?date={date}&station={station}&product={product}&format={format}&units={units}&application={application}&time_zone={time_zone}&datum={datum}" 

    if interval is not None:
        url = f"{url}&interval={interval}"

    return url

def call_api(date:str = "today",
    product:str = "predictions",
    station:str = "8511907",
    format:str = "json",
    application:str = "LED_Matrix",
    units:str = "english",
    time_zone:str = "lst_ldt",
    datum:str = "MLLW",
    interval:str|None=None):# -> Any | dict[Any, Any]:
    
    url:str = get_api_url(date=date, product=product, station=station, format=format, application=application, units=units, time_zone=time_zone, datum=datum, interval=interval)
    try:
        print(f"call {url}")
        response: requests.Response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(response)
            print(response.json())
            
    except Exception as e:
        print(f"Unable to get tides info, {e}")
    return {}


def get_station_name():
    url:str = get_api_url(product="wind", format="xml")
    try:
        print(f"call {url}")
        response: requests.Response = requests.get(url, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.text)

            meta: ET.Element | None = root.find("metadata")
            station_name = meta.get("name")
            return station_name
        else:
            return None
        
    except Exception as e:
        print(f"Unable to get station info, {e}")
    return None
    
def get_tide_data_for_plot(w=5):
    raw_data = call_api()["predictions"]
    min_v:float=0
    max_v:float=0
    
    data = []
    
    for entry in raw_data:
        t:str = entry["t"].split(" ")[-1]
        
        v:float = float(entry["v"])
        if v > max_v:
            max_v=v
        if v < min_v:
            min_v = v
        data.append((t,v))
    
    delta_v:float = int(SINUS_HEIGHT/(max_v-min_v))
    delta_t:float = w*64.0/len(data)
    
    print(f"delta_t={delta_t}")
    print(f"delta_v={delta_v}")
    Y_offset:int = int((64 - SINUS_HEIGHT)/2)
    
    curve:list[tuple[int, int]] = []
    timeline:list[str]=[]
    
    for idx, entry in enumerate(data):
        
        x:int = int(idx*delta_t)
        y:int = Y_offset + int(delta_v * (entry[1]-min_v))

        curve.append((x,y))
        timeline.append(entry[0])
        
    return {"curve" : curve, "timeline": timeline, "delta_v": delta_v, "delta_t":delta_t, "Y_offset": Y_offset, "min_v": min_v}

def find_x(curve, timeline, target_time):
    
    print(f"Calling find_x with target_time={target_time}")
    if isinstance(target_time, str):    
        target_time =  datetime.strptime(target_time, "%H:%M")

    for idx, d in enumerate(timeline):
        
        t1 = datetime.strptime(d, "%H:%M")
        if t1 > target_time:
            t0 = datetime.strptime(timeline[idx-1], "%H:%M")
            
            interval_delta = t1-t0
            interval_delta_s = interval_delta.total_seconds()
            
            t_delta = target_time-t0
            t_delta_s = t_delta.total_seconds()
            
            ratio = t_delta_s/interval_delta_s
            
            x0 = curve[idx-1][0]
            x1 = curve[idx][0]
            
            x = int(x0 + (x1-x0) * ratio)
            return x
    
    return None
            
            
def get_tide_data(w=5):
    
    station_name:str|None = get_station_name()
    result = get_tide_data_for_plot()
    
    Y_offset:int = result["Y_offset"]
    min_v:float = result["min_v"]
    delta_v:float = result["delta_v"]
    hilo_raw = call_api(interval="hilo")["predictions"]
    curve= result["curve"]
    timeline = result["timeline"]
        
    hilo = []
    for entry in hilo_raw:
        t = entry["t"]
        v = float(entry["v"])
        type = entry ["type"]    
        
        y:int = Y_offset + int(delta_v * (v-min_v))

        t = t.split(" ")[-1]
        x=find_x(curve, timeline, target_time=t)

        hilo.append({"t":t, "v":v, "y":y, "type":type, "x": x })
    

    x_now=find_x(curve, timeline, target_time=datetime.now().strftime("%H:%M"))
    
    return {
        "name": station_name,
        "curve": curve,
        "timeline": timeline,
        "hilo" : hilo,
        "x_now" : x_now
    }
    
if __name__ == "__main__":
    #print(json.dumps(get_tide_data(), indent=4))
    #get_tide_data_as_arrays()
    print(get_tide_data())