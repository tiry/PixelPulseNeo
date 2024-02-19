import requests

GLOBAL_ENDPOINTG = "https://api.citybik.es/v2/networks"
NYC_ENDPOINT = "https://api.citybik.es//v2/networks/citi-bike-nyc"

# Custom headers
headers = {}


def isMatch(keywords, name) -> bool:
    target = name.lower()
    for kw in keywords:
        if kw.lower() not in target:
            return False
    return True


def getStationInfo(keywords:list[str]=["Columbia"]) -> list[dict]:    
    # Send the GET request
    response = requests.get(NYC_ENDPOINT, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        matches = []

        stations = data["network"]["stations"]
        for station in stations:
            if isMatch(keywords, station["name"]):
                matches.append(
                    {
                        "name": station["name"],
                        "empty": station["empty_slots"],
                        "free_bikes": station["free_bikes"],
                        "ebikes": station["extra"]["ebikes"],
                    }
                )

        return matches
    else:
        print(f"Failed to retrieve data: Status code {response.status_code}")
        return []

