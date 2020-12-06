#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W0613

'''
    Map Server
'''

import sys
import json
import argparse
from random import choice

import Ice
Ice.loadSlice('IceGauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

ROOMS_FILE = 'rooms.json'

class MapManIntermediary(IceGauntlet.MapManagement):
    '''Map Management Servant'''
    def __init__(self, broker, args):
        '''Conecting with the Authentication Server'''
        try:
            self.communicator = broker
            self.auth_proxy = self.communicator.stringToProxy(args.authProxy)
            self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(self.auth_proxy)
            #print("\nTe has conectado al Proxy: " + args.authProxy)

            if not self.auth_server:
                raise RuntimeError('Invalid proxy')
        except Ice.Exception:
            print("Proxy no disponible en este momento\nException: Connection Refused")

    def publish(self, token, room_data, current=None):
        '''Publish a room'''
        if not self.auth_server.isValid(token):
            raise IceGauntlet.Unauthorized()
        self.__commit__(token, room_data)

    def remove(self, token, room_name, current=None):
        '''Remove a room'''
        if not self.auth_server.isValid(token):
            raise IceGauntlet.Unauthorized()
        self.__uncommit__(token, room_name)

    @staticmethod
    def __commit__(token, room_data):
        '''Saves the map in the rooms.json file'''
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        new_room = json.loads(room_data)

        try:
            __rooms__ = rooms.keys()

            if len(__rooms__) != 0:
                if new_room["room"] in __rooms__:
                    if token != rooms[list(new_room["room"].keys())[0]]:
                        raise IceGauntlet.RoomAlreadyExists()
        except KeyError:
            raise IceGauntlet.WrongRoomFormat()

        rooms[new_room["room"]] = {}
        rooms[new_room["room"]][token] = {}
        rooms[new_room["room"]][token] = new_room

        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)

    @staticmethod
    def __uncommit__(token, room_name):
        '''Removes the map from the rooms.json file'''
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        if not room_name in rooms:
            raise IceGauntlet.RoomNotExists()

        if token != list(rooms[room_name].keys())[0]:
            raise IceGauntlet.RoomNotExists()

        rooms.pop(room_name)

        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)

class GameService(IceGauntlet.Game):
    '''Game Servant'''
    def getRoom(self, current=None):
        '''Returns a random room'''
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        __rooms__ = rooms.keys()

        if len(__rooms__) == 0:
            raise IceGauntlet.RoomNotExists

        selected_room = choice(list(__rooms__))
        selected_room_token = rooms[selected_room].keys()
        room_data_dict = rooms[selected_room][list(selected_room_token)[0]]
        room_data = json.dumps(room_data_dict)

        return room_data

class MapManServer(Ice.Application):
    '''Map Server'''
    def run(self, argv):
        args = self.parse_args(argv)
        broker = self.communicator()
        map_man_servant = MapManIntermediary(broker, args)
        game_servant = GameService()

        adapter = broker.createObjectAdapter("MapAdapter")
        map_man_proxy = adapter.add(map_man_servant, broker.stringToIdentity('mapManService'))
        game_proxy = adapter.add(game_servant, broker.stringToIdentity('gameService'))

        #print("Proxy del servicio de Gestión de Mapas: ")
        print('"{}"'.format(map_man_proxy))
        #print("Proxy del servicio de Juego: ")
        self.save_game_proxy('"{}"'.format(game_proxy))

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

    @staticmethod
    def parse_args(argv):
        '''Parse the arguments'''
        parser = argparse.ArgumentParser()
        parser.add_argument("authProxy", help="Proxy generado por el Athentication Server")
        args = parser.parse_args()
        return args

    @staticmethod
    def save_game_proxy(game_proxy):
        '''Save the game service proxy in gameProxy.txt'''
        game_proxy_txt = open("gameProxy.txt", "w")
        game_proxy_txt.write(game_proxy)
        game_proxy_txt.close()

if __name__ == '__main__':
    APP = MapManServer()
    sys.exit(APP.main(sys.argv))
