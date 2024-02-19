
# API

The API used are `https://api.citybik.es/v2/networks` and more specificaly 
`https://api.citybik.es//v2/networks/citi-bike-nyc`

## Running as command line

     python -m Matrix.driver.commands.citibikes_cmd

## Configuring

The target Station is configured using a list of strings.

### Query the API to locate the station

You can use the Command Line to locate your station:

    python -m Matrix.driver.commands.citibikes_cmd -q Columbia

      Station : Columbia St & W 9 St
      Station : Columbia St & Kane St
      Station : Columbia Heights & Cranberry St
      Station : Sigourney St & Columbia St
      Station : Columbia St & Degraw St
      Station : Columbia St & Rivington St
      Station : Carroll St & Columbia St
      Station : E Houston St & Columbia St
      Station : Columbia St & Lorraine St

    python -m Matrix.driver.commands.citibikes_cmd -q Columbia Degraw

      Station : Columbia St & Degraw St

Once you have found the correct list of keywords, you can update the configuration.

### Update configuration


Configuration is handled by [config.py](../../../config.py).


    CITIBIKES: list[str] = ["Columbia", "Carroll"]


