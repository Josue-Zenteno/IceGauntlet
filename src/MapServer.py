#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W1203
# pylint: disable=W0613

import sys
import Ice
import json
import argparse
from random import choice
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

    def publish(self, token, roomData, current = None):
        '''Publish a room'''
        if not self.authServer.isValid(token):
            raise IceGauntlet.Unauthorized()
        self.__commit__(token, roomData)
        
    def remove(self, token, roomName, current = None):
        '''Remove a room'''
        if not self.authServer.isValid(token):
            raise IceGauntlet.Unauthorized()
        self.__uncommit__(token, roomName)

    @staticmethod   
    def __commit__(token, roomData):
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        newRoom = json.loads(roomData)
        
        __rooms__ = rooms.keys()
        
        if len(__rooms__) != 0:
            if newRoom["room"] in __rooms__:
                if token != rooms[newRoom["room"]]:
                    raise IceGauntlet.RoomAlreadyExists()

        rooms[newRoom["room"]]= {}
        rooms[newRoom["room"]][token] = {}
        rooms[newRoom["room"]][token] = newRoom

        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)
    
    @staticmethod
    def __uncommit__(token, roomName):
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        if not roomName in rooms:
            raise IceGauntlet.RoomNotExists()
        else:
            if token != rooms[roomName]:
                raise IceGauntlet.RoomNotExists() 

        rooms.pop(roomName)

        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)
            
class GameService(IceGauntlet.Game):
    def getRoom(self, current = None):
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)
        
        __rooms__ = rooms.keys()
        
        if len(__rooms__) == 0:
            raise IceGauntlet.RoomNotExists

        selectedRoom = choice(list(__rooms__))
        selectedRoomToken = rooms[selectedRoom].keys()
        roomDataDict = rooms[selectedRoom][list(selectedRoomToken)[0]]
        roomData = json.dumps(roomDataDict)
        
        return roomData

class MapManServer(Ice.Application):
    def run(self, argv):
        args = self.parseArgs(argv)
        broker = self.communicator()
        mapManServant = MapManIntermediary(broker, args)
        gameServant = GameService()

        adapter =  broker.createObjectAdapter("MapAdapter")
        mapManProxy = adapter.add(mapManServant, broker.stringToIdentity('mapManService'))
        gameProxy = adapter.add(gameServant, broker.stringToIdentity('gameService')) 
        
        print("Proxy del servicio de Gestión de Mapas: ")
        print('"{}"'.format(mapManProxy), flush=True)
        print("Proxy del servicio de Juego: ")
        print('"{}"'.format(gameProxy), flush=True)

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