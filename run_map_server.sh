#!/bin/bash
if [ $# -gt 0 ] 
then
    python3 ./src/map_server.py --Ice.Config=./src/map_server.config "$1"
else
    echo "Command arguments: <auth_proxy>"
fi
