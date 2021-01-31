#!/bin/bash
mkdir -p /tmp/IceGauntlet/
cp -r server2.py icegauntlet_auth_server/auth_server icegauntlettool.py icegauntlet.ice rooms/ icegauntlet_auth_server/users.json IceStorm/ /tmp/IceGauntlet/
icepatch2calc /tmp/IceGauntlet/