#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W1203
# pylint: disable=W0613

import sys
import Ice
import json
import argparse
Ice.loadSlice('IceGauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

ROOMS_FILE = 'rooms.json'

class MapManIntermediary(IceGauntlet.MapManagement):
    def __init__(self, broker, args):
        '''Conecting with the Authentication Server'''
        try:
            self.communicator = broker
            self.authProxy = self.communicator.stringToProxy(args.authProxy)
            self.authServer = IceGauntlet.AuthenticationPrx.checkedCast(self.authProxy)
            print("\nTe has conectado al Proxy: " + args.authProxy)

            if not self.authServer:
                raise RuntimeError('Invalid proxy') 

        except Ice.Exception:
            print("Proxy no disponible en este momento\nException: Connection Refused")

    def publish(self, token, roomData):
        '''Publish a room'''
        if not self.authServer.isValid(token):
            raise IceGauntlet.Unauthorized()
        self.__commit__(token, roomData)
        
    
    def remove(self, token, roomName):
        '''Remove a room'''
        if not self.authServer.isValid(token):
            raise IceGauntlet.Unauthorized()
        self.__uncommit__(roomName)

    @staticmethod   
    def __commit__(token, roomData):
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        newRoom = json.loads(roomData)
        
        if rooms[newRoom["room"]][token] != token:
            raise IceGauntlet.RoomAlreadyExists()

        rooms[newRoom["room"]][token] = newRoom

        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)
    
    @staticmethod
    def __uncommit__(roomName):
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        if not roomName in rooms:
            raise IceGauntlet.RoomNotExists() 

        rooms.pop("roomName")

        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)
class MapManServer(Ice.Application):
    def run(self, argv):
        args = self.parseArgs(argv)
        broker = self.communicator()
        servant = MapManIntermediary(broker, args)
        
        adapter =  broker.createObjectAdapter("MapManagementAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity('default'))

        print("Proxy de este servicio: ")
        print('"{}"'.format(proxy), flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

    @staticmethod
    def parseArgs(argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("authProxy", help="Aqui va el proxy generado por el Athentication Server")
        args = parser.parse_args()
        return args

if __name__ == '__main__':
    app = MapManServer()
    sys.exit(app.main(sys.argv))