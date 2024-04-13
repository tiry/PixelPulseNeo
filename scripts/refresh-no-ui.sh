#!/bin/bash


# Git

echo "**************************************"
echo "Pull updates from Git"

git pull

# restart services

echo "**************************************"
echo "Restarting services"

sudo systemctl stop pixel-pulse-neo-api

sudo systemctl stop pixel-pulse-neo

sudo systemctl start pixel-pulse-neo-api
