# About

This folder contains Unit descriptors for SystemD init system.

# Install the systemd files

## Deployment

The `deploy` script must be started from the root directory (as normal user)

    ./system/deploy.sh

This will :

 - generate the service files from the templates
 - copy the service files to `/lib/systemd/system/` 
 - call  `systemctl daemon-reload`

For all this to work, you should have created `/etc/PixelPulseNeo/secrets.conf` and filled it with your configuration.

For that you can use the provided `init-config.sh` as documented in [Config.md](../Config.md).


## Units

We are declating 2 Systemd Units/Services:

 - `pixel-pulse-neo.service`: the command server
    - run as ROOT
 - `pixel-pulse-neo-api.service`: the web server (Rest API + Web UI)
    - run as unpriviledged user (`tiry`)

`pixel-pulse-neo-api.service` has a dependency on `pixel-pulse-neo.service`

starting `pixel-pulse-neo-api.service` will automatically start `pixel-pulse-neo.service` too.

# Using Systemd

## Start

    sudo systemctl start pixel-pulse-neo-api

## Get status

    systemctl status pixel-pulse-neo

    systemctl status pixel-pulse-neo-api

## Stop

    sudo systemctl stop pixel-pulse-neo-api

    sudo systemctl stop pixel-pulse-neo

## Make the services run automatically on boot

    sudo systemctl enable pixel-pulse-neo-api


## Get logs

    sudo journalctl -u pixel-pulse-neo-api -f

    sudo journalctl -u pixel-pulse-neo -f
    
    sudo journalctl -u pixel-pulse-neo  --since "1 hour ago" > last-hour.log
    
