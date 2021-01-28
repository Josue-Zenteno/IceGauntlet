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
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

ROOMS_FILE = 'rooms.json'

class RoomManager(IceGauntlet.RoomManager):
    '''Room Manager Servant'''
    def __init__(self, broker, args):
        '''Conecting with the Authentication Server'''
        self.map_storage = MapStorage()
        try:
            self.communicator = broker
            self.auth_proxy = self.communicator.stringToProxy(args.authProxy)
            self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(self.auth_proxy)
            if not self.auth_server:
                raise RuntimeError('Invalid proxy')
        except Ice.Exception:
            print("Proxy no disponible en este momento\nException: Connection Refused")

    def publish(self, token, room_data, current=None):
        '''Publish a room'''
        user_name = self.auth_server.getOwner(token)
        if not user_name:
            raise IceGauntlet.Unauthorized()
        self.map_storage.__commit__(user_name, room_data)
        
    def remove(self, token, room_name, current=None):
        '''Remove a room'''
        user_name = self.auth_server.getOwner(token)
        if not user_name:
            raise IceGauntlet.Unauthorized()
        self.map_storage.__uncommit__(user_name, room_name)
    
    def availableRooms(self):
        '''Returns a list of all the rooms in this RoomManager'''
        pass #TODO

    @staticmethod
    def getRoom(roomName, current=None):
        '''Returns a random room'''
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)
        __rooms__ = rooms.keys()

        if len(__rooms__) == 0:
            raise IceGauntlet.RoomNotExists

        if roomName not in __rooms__:
            raise IceGauntlet.RoomNotExists

        user_name = rooms[roomName].keys()
        room_data_dict = rooms[roomName][list(user_name)[0]]
        room_data = json.dumps(room_data_dict)

        return room_data

class Dungeon(IceGauntlet.Dungeon):
    '''Dungeon Servant'''
    pass

class DungeonArea(IceGauntlet.DungeonArea):
    '''DungeonArea Servant'''
    pass

class MapStorage:
    @staticmethod
    def __commit__(user_name, room_data):
        '''Saves the map in the rooms.json file'''
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        new_room = json.loads(room_data)

        try:
            __rooms__ = rooms.keys()

            if len(__rooms__) != 0:
                if new_room["room"] in __rooms__:
                    if user_name != rooms[list(new_room["room"].keys())[0]]:
                        raise IceGauntlet.RoomAlreadyExists()
        except KeyError:
            raise IceGauntlet.WrongRoomFormat()

        rooms[new_room["room"]] = {}
        rooms[new_room["room"]][user_name] = {}
        rooms[new_room["room"]][user_name] = new_room

        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)

    @staticmethod
    def __uncommit__(user_name, room_name):
        '''Removes the map from the rooms.json file'''
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)

        if not room_name in rooms:
            raise IceGauntlet.RoomNotExists()

        if user_name != list(rooms[room_name].keys())[0]:
            raise IceGauntlet.RoomNotExists()

        rooms.pop(room_name)

        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)

class MapManServer(Ice.Application):
    '''Map Server'''
    def run(self, argv):
        args = self.parse_args(argv)
        broker = self.communicator()

        room_manager_servant = RoomManager(broker, args)
        dungeon_servant = Dungeon() #TODO
        #dungeon_area_servant = DungeonArea() #TODO

        adapter = broker.createObjectAdapter("RoomManagerAdapter")
        map_man_proxy = adapter.addWithUUID(room_manager_servant)
        game_proxy = adapter.addWithUUID(dungeon_servant)

        print('"{}"'.format(map_man_proxy))
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
