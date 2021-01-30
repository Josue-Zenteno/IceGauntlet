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
        return self.map_storage.get_rooms_with_users()

    def getRoom(self, room_name, current=None):
        '''Returns the room information'''
        if room_name not in self.map_storage.get_rooms():
            raise IceGauntlet.RoomNotExists()
        return self.map_storage.get_room_data(room_name)

class Dungeon(IceGauntlet.Dungeon):
    '''Dungeon Servant'''
    pass

class DungeonArea(IceGauntlet.DungeonArea):
    '''DungeonArea Servant'''
    pass

class MapStorage:
    @staticmethod
    def open_db():
        '''Reads the JSON file Rooms.json'''
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)
        return rooms
    
    @staticmethod
    def write_db(rooms):
        '''Overwrites the JSON file Rooms.json'''
        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)

    def __commit__(self, user_name, room_data):
        '''Saves the map in the rooms.json file'''
        rooms = self.open_db()
        new_room = json.loads(room_data)

        try:
            __rooms__ = rooms.keys()

            if len(__rooms__) != 0:
                if new_room["room"] in __rooms__:
                    new_room_name = new_room[list(new_room.keys())[1]]
                    if user_name != list(rooms[new_room_name].keys())[0]:
                        raise IceGauntlet.RoomAlreadyExists()
        except KeyError:
            raise IceGauntlet.WrongRoomFormat()

        rooms[new_room["room"]] = {}
        rooms[new_room["room"]][user_name] = {}
        rooms[new_room["room"]][user_name] = new_room

        self.write_db(rooms)

    def __uncommit__(self, user_name, room_name):
        '''Removes the map from the rooms.json file'''
        rooms = self.open_db()

        if room_name not in rooms:
            raise IceGauntlet.RoomNotExists()
        if user_name != list(rooms[room_name].keys())[0]:
            raise IceGauntlet.RoomNotExists()
        rooms.pop(room_name)

        self.write_db(rooms)

    def get_rooms(self):
        '''Returns a list with all the room names'''
        rooms = self.open_db()
        return list(rooms.keys())

    def get_rooms_with_users(self):
        '''Returns a list with the format:[{Room:User}, ...]'''
        rooms = self.open_db()

        rooms_and_users_list = list()

        for room in list(rooms.keys()):
            dictionary = {}
            dictionary[room] = {}
            dictionary[room] = list(rooms[room].keys())[0]
            rooms_and_users_list.append(json.dumps(dictionary))

        return rooms_and_users_list

    def get_room_data(self, roomName):
        '''Returns the information of an specific room given the name'''
        rooms = self.open_db()

        user_name = list(rooms[roomName].keys())[0]
        return json.dumps(rooms[roomName][user_name])

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
