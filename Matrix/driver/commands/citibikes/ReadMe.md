
# API

The API used are `https://api.citybik.es/v2/networks` and more specificaly 
`https://api.citybik.es//v2/networks/citi-bike-nyc`

## Running as command line

To run as command line you first need to be sure to have activate the python virtual env.

If you followed the install instructions, you can use:

    source venv/bin/activate

Your shell should then display: 

    (venv) JeanSe@LEDJeanSe:~/dev/PixelPulseNeo 

From there you should be able to the CLI to configure the `citibikes_cmd`

     python -m Matrix.driver.commands.citibikes_config

## Configuring

The target Station is configured using a list of strings.

### Query the API to locate the station

You can use the Command Line to locate your station:

    python -m Matrix.driver.commands.citibikes_config -q Columbia

      Station : Columbia St & W 9 St
      Station : Columbia St & Kane St
      Station : Columbia Heights & Cranberry St
      Station : Sigourney St & Columbia St
      Station : Columbia St & Degraw St
      Station : Columbia St & Rivington St
      Station : Carroll St & Columbia St
      Station : E Houston St & Columbia St
      Station : Columbia St & Lorraine St

    python -m Matrix.driver.commands.citibikes_config -q henry
 
      Station : Henry St & Middagh St
      Station : Henry St & W 9 St
      Station : Henry St & Atlantic Ave
      Station : Henry St & Bay St
      Station : Henry St & Remsen St
      Station : Richardson St & N Henry St
      Station : Rutgers St & Henry St
      Station : Clark St & Henry St
      Station : President St & Henry St
      Station : Market St & Henry St
      Station : N Henry St & Norman Ave
      Station : Driggs Ave & N Henry St
      Station : Henry St & Degraw St
      Station : Henry St & Grand St

    python -m Matrix.driver.commands.citibikes_config -q Columbia Carroll

      Station : Carroll St & Columbia St

Once you have found the correct list of keywords, you can update the configuration.

### Update configuration

Configuration is handled by [config.py](../../../config.py).


    CITIBIKES: list[str] = ["Columbia", "Carroll"]


