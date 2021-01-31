#!/bin/bash
mkdir -p /tmp/icegauntlet/
cp -r icegauntlet.ice src/map_server.py src/auth_server.py rooms.json users.json managers.json IceStorm/ /tmp/icegauntlet/
icepatch2calc /tmp/icegauntlet/