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
import IceStorm
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

ROOMS_FILE = 'rooms.json'
MANAGERS_FILE = 'managers.json'
ROOM_MANAGER_PROXY = ''
class RoomManager(IceGauntlet.RoomManager):
    '''Room Manager Servant'''
    def __init__(self, broker, publisher, args):
        '''Conecting with the Authentication Server'''
        self.map_storage = MapStorage()
        self.publisher = publisher
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
        room_name = self.map_storage.commit_room(user_name, room_data)
        self.publisher.newRoom(room_name, '{}'.format(ROOM_MANAGER_PROXY))

    def remove(self, token, room_name, current=None):
        '''Remove a room'''
        user_name = self.auth_server.getOwner(token)
        if not user_name:
            raise IceGauntlet.Unauthorized()
        self.map_storage.uncommit_room(user_name, room_name)
        self.publisher.removedRoom(room_name)

    def availableRooms(self, current=None):
        '''Returns a list of all the rooms in this RoomManager'''
        return self.map_storage.get_rooms_with_users()

    def getRoom(self, room_name, current=None):
        '''Returns the room information'''
        if room_name not in self.map_storage.get_rooms():
            raise IceGauntlet.RoomNotExists()
        return self.map_storage.get_room_data(room_name)

class RoomManagerSync(IceGauntlet.RoomManagerSync):
    '''Event channel for Room Manager synchronization'''

    def __init__(self, publisher, broker):
        self.managers_storage = MapStorage()
        self.publisher = publisher
        self.communicator = broker

    def hello(self, manager, managerId, current=None):
        '''Sends a hello message'''
        if managerId != '{}'.format(ROOM_MANAGER_PROXY):
            if managerId not in self.managers_storage.get_managers():
                self.managers_storage.commit_manager(managerId)
        self.publisher.announce(IceGauntlet.RoomManagerPrx.uncheckedCast(ROOM_MANAGER_PROXY),'{}'.format(ROOM_MANAGER_PROXY))

    def announce(self, manager, managerId, current=None):
        '''Sends an announce message'''
        if managerId != '{}'.format(ROOM_MANAGER_PROXY):
            if managerId not in self.managers_storage.get_managers():
                self.managers_storage.commit_manager(managerId)
        
    def newRoom(self, roomName, managerId, current=None):
        '''Sends a new room message'''
        if roomName not in self.managers_storage.get_rooms():
            print(managerId)
            manager_proxy = self.communicator.stringToProxy(managerId)
            manager = IceGauntlet.RoomManagerPrx.checkedCast(manager_proxy)
            
            remote_available_rooms = manager.availableRooms()
            local_available_rooms = self.managers_storage.get_rooms_with_users()
            
            if remote_available_rooms != local_available_rooms:
                new_rooms = list()
                for room in remote_available_rooms:
                    if room not in local_available_rooms:
                        new_rooms.append(room)

            for room in new_rooms:
                aux_dict = json.loads(room)
                room_name = list(aux_dict.keys())[0]
                user_name = aux_dict[room_name]
                room_data = manager.getRoom(roomName)
                self.managers_storage.commit_room_event(user_name, room_data)

    def removedRoom(self, roomName, current=None):
        '''Sends a removed room message'''
        if roomName in self.managers_storage.get_rooms():
            self.managers_storage.uncommit_room_event(roomName)

class Dungeon(IceGauntlet.Dungeon):
    '''Dungeon Servant'''
    def getEntrance(self, current=None):
        '''Returns a DungeonArea'''
        pass

class DungeonArea(IceGauntlet.DungeonArea):
    '''DungeonArea Servant'''
    def getEventChannel(self, current=None):
        '''Returns the event channel'''
        pass

    def getMap(self, current=None):
        '''Returns the map'''
        pass

    def getActors(self, current=None):
        '''Returns the cast ?'''
        pass

    def getItems(self, current=None):
        '''Returns the items ?'''
        pass

    def getNextArea(self, current=None):
        '''Returns the next DungeonArea'''
        pass

class DungeonAreaSync():
    '''Event channel for DungeonArea synchronization'''    
    def fireEvent(self, event, senderId, current=None):
        '''Sends Fire Event'''
        pass

class MapStorage:
    @staticmethod
    def open_rooms_db():
        '''Reads the JSON file Rooms.json'''
        with open(ROOMS_FILE, 'r') as roomsfile:
            rooms = json.load(roomsfile)
        return rooms
    
    @staticmethod
    def write_rooms_db(rooms):
        '''Overwrites the JSON file Rooms.json'''
        with open(ROOMS_FILE, 'w') as roomsfile:
            json.dump(rooms, roomsfile, indent=4)

    @staticmethod
    def open_managers_db():
        '''Reads the JSON file Rooms.json'''
        with open(MANAGERS_FILE, 'r') as managersfile:
            managers = json.load(managersfile)
        return managers
    
    @staticmethod
    def write_managers_db(managers):
        '''Overwrites the JSON file Rooms.json'''
        with open(MANAGERS_FILE, 'w') as managersfile:
            json.dump(managers, managersfile, indent=4)

    def commit_room(self, user_name, room_data):
        '''Saves the map in the rooms.json file'''
        rooms = self.open_rooms_db()
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

        self.write_rooms_db(rooms)

        return new_room["room"]

    def uncommit_room(self, user_name, room_name):
        '''Removes the map from the rooms.json file'''
        rooms = self.open_rooms_db()

        if room_name not in rooms:
            raise IceGauntlet.RoomNotExists()
        if user_name != list(rooms[room_name].keys())[0]:
            raise IceGauntlet.RoomNotExists()
        rooms.pop(room_name)

        self.write_rooms_db(rooms)

    def commit_room_event(self, user_name, room_data):
        '''Saves the map in the rooms.json file'''
        rooms = self.open_rooms_db()
        new_room = json.loads(room_data)

        if new_room["room"] not in list(rooms.keys()):
            rooms[new_room["room"]] = {}
            rooms[new_room["room"]][user_name] = {}
            rooms[new_room["room"]][user_name] = new_room

        self.write_rooms_db(rooms)

    def uncommit_room_event(self, room_name):
        '''Removes the map from the rooms.json file'''
        rooms = self.open_rooms_db()
        rooms.pop(room_name)
        self.write_rooms_db(rooms)

    def get_rooms(self):
        '''Returns a list with all the room names'''
        rooms = self.open_rooms_db()
        return list(rooms.keys())

    def get_rooms_with_users(self):
        '''Returns a list with the format:[{Room:User}, ...]'''
        rooms = self.open_rooms_db()

        rooms_and_users_list = list()

        for room in list(rooms.keys()):
            dictionary = {}
            dictionary[room] = {}
            dictionary[room] = list(rooms[room].keys())[0]
            rooms_and_users_list.append(json.dumps(dictionary))

        return rooms_and_users_list

    def get_room_data(self, roomName):
        '''Returns the information of an specific room given the name'''
        rooms = self.open_rooms_db()

        user_name = list(rooms[roomName].keys())[0]
        return json.dumps(rooms[roomName][user_name])

    def commit_manager(self, manager_id):
        '''Saves the identifier of a RoomManager'''
        managers = self.open_managers_db()
        managers[manager_id] = {}
        self.write_managers_db(managers)

    def get_managers(self):
        '''Returns a list with all the RoomManager IDs'''
        managers = self.open_managers_db()
        return list(managers.keys()) 

class MapManServer(Ice.Application):
    '''Map Server'''
    def run(self, argv):
        args = self.parse_args(argv)
        broker = self.communicator()
        topic_mgr = self.get_topic_manager(broker)
        adapter = broker.createObjectAdapter("RoomManagerAdapter")
        
        topic = self.prepare_topic(topic_mgr)
        publisher = self.prepare_publisher(topic)
        subscriber = self.prepare_subscriber(adapter, topic, broker, publisher)
        
        global ROOM_MANAGER_PROXY
        room_manager_servant = RoomManager(broker, publisher, args) 
        ROOM_MANAGER_PROXY = adapter.addWithUUID(room_manager_servant)
        
        publisher.hello(IceGauntlet.RoomManagerPrx.uncheckedCast(ROOM_MANAGER_PROXY),'{}'.format(ROOM_MANAGER_PROXY))

        dungeon_servant = Dungeon()
        dungeon_proxy = adapter.addWithUUID(dungeon_servant)

        print('"{}"'.format(ROOM_MANAGER_PROXY))
        self.save_game_proxy('"{}"'.format(dungeon_proxy))

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        topic.unsubscribe(subscriber)
        return 0
    
    @staticmethod
    def prepare_topic(topic_mgr):
        topic_name = "RoomManagerSyncChannel"
        try:
            topic = topic_mgr.retrieve(topic_name)
        # pylint: disable=E1101
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)
        return topic

    @staticmethod
    def prepare_subscriber(adapter, topic, broker, publisher):
        room_manager_sync_servant = RoomManagerSync(publisher, broker)
        subscriber = adapter.addWithUUID(room_manager_sync_servant)
        topic.subscribeAndGetPublisher({}, subscriber)
        return subscriber

    @staticmethod
    def prepare_publisher(topic):
        publisher_prx = topic.getPublisher()
        publisher = IceGauntlet.RoomManagerSyncPrx.uncheckedCast(publisher_prx)
        return publisher

    @staticmethod
    def get_topic_manager(broker):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = broker.propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return None
        # pylint: disable=E1101
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

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