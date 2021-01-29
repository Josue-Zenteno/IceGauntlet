#!/bin/bash
if [ $# -gt 2 ] 
then
    python3 ./src/map_client.py "$1" "$2" -p "$3"
else
    echo "Command arguments: <map_proxy> <token> <map_file>"
fi