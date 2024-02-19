# Using MTA API

## API Keys

To Access the MTA API you need to get API Keys.

See http://web.mta.info/developers/

You will basically need to register against https://api.mta.info/

Once you have a developer account you can:

 - create an API Access Key
 - you can ask for a SIRI API Access Key

The SIRI API Key is deliverd via email.

The MTA Command expect to find the 2 following env variables.

    MTA_API_KEY=.....

    MTA_SIRI_API_KEY=......

## Running as command line

     python -m Matrix.driver.commands.mta_cmd

## Configuring

The target Station is configured using a list of strings.

### Query the API to locate the station

You can use the Command Line to locate your station:

#### Subway 

Query for Station with "Carroll" in their name

    python -m Matrix.driver.commands.mta_cmd  -s Carroll

     stop_name = Carroll St (F21N)
     stop_name = Carroll St (F21S)

Query for Station with "Wash" in their name

    python -m Matrix.driver.commands.mta_cmd -s Wash

     stop_name = 168 St-Washington Hts (112N)
     stop_name = 168 St-Washington Hts (112S)
     stop_name = W 4 St-Wash Sq (A32N)
     stop_name = W 4 St-Wash Sq (A32S)
     stop_name = Clinton-Washington Avs (A44N)
     stop_name = Clinton-Washington Avs (A44S)
     stop_name = W 4 St-Wash Sq (D20N)
     stop_name = W 4 St-Wash Sq (D20S)
     stop_name = Clinton-Washington Avs (G35N)
     stop_name = Clinton-Washington Avs (G35S)

You can add 2 parameters to specify the info you want:

 - the direction `N` or `S` using `-d`
 - the routes you want (`F`, `G`, `C`) using the `-r` argument


For example, to get the next `D` train direction North on station W 4 St-Wash Sq

    python -m Matrix.driver.commands.mta_cmd -r D -d N  -s Wash

      Next trains for D station Wash on direction N
        13:14
        13:24
        13:33

#### Bus

Query for bus libe B61

    python -m Matrix.driver.commands.mta_cmd -b B61
      search bus line
      Found MTA NYCT_B61

Query for Station Carroll on B61

    python -m Matrix.driver.commands.mta_cmd -b B61 -s Carroll
      search bus stop line
      PARK SLOPE 20 ST via RED HOOK:
        13:31
        13:47
        13:59
        14:11
        14:32*
      DOWNTOWN BKLYN FULTON MALL via RED HOOK:
        13:33
        13:46
        13:52
        14:09
        14:45*
        14:57*

The command line should allow to deternine the 5 configurations parameters you will need to add to [config.py](../../../config.py).

### Update configuration


    MTA_SUBWAY_STATION:str = "Carroll"
    MTA_SUBWAY_DIRECTION:str = "N"
    MTA_SUBWAY_ROUTES:list[str] = ["F","G"]

    MTA_BUS_STATION:str = "Carroll"
    MTA_BUS_LINE:str = "B61"

