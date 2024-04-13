#!/bin/bash

export PPNPATH=${PWD}
export OWNER=`whoami`

echo "Configuring pixel-pulse-neo services with user='$OWNER' and path='$PPNPATH'"

#envsubst < system/pixel-pulse-neo-api.service.template 
envsubst < system/pixel-pulse-neo-api.service.template > /tmp/pixel-pulse-neo-api.service

#envsubst < system/pixel-pulse-neo.service.template 
envsubst < system/pixel-pulse-neo.service.template > /tmp/pixel-pulse-neo.service


sudo cp /tmp/pixel*.service /lib/systemd/system/.
#sudo cp /tmp/pixel*.service /tmp/yo/.

sudo systemctl daemon-reload

