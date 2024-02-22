#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
HOME_DIR=$(dirname $(realpath $SCRIPT_DIR))



echo "SCRIPT_DIR directory: $SCRIPT_DIR"
echo "PPN directory: $HOME_DIR"