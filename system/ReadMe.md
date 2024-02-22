# About

This folder contains Unit descriptors for SystemD init system.

# Install the systemd files

## Deployment

    ./deploy.sh

This will copy the service files to `/lib/systemd/system/` and call  `systemctl daemon-reload`

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


## Get logs

    sudo journalctl -u pixel-pulse-neo-api

    sudo journalctl -u pixel-pulse-neo
    
