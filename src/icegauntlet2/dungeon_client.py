#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''
    ICE Gauntlet ONLINE GAME
'''

import sys
import atexit
import argparse
import json

import Ice
Ice.loadSlice('IceGauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

import game
import game.common
import game.screens
import game.pyxeltools
import game.orchestration


EXIT_OK = 0
BAD_COMMAND_LINE = 1

DEFAULT_ROOM = 'tutorial.json'
DEFAULT_HERO = game.common.HEROES[0]

class RemoteDungeonMap(Ice.Application):
    '''Remote Dungeon Map'''
    def __init__(self):
        self._levels_ = list()

    def run(self, game_proxy):
        try:
            #gameProxy = input("Introduce el Proxy del servicio de juego: ")
            cantidad_de_mapas = input("Cuantos mapas quieres jugar:")
            proxy = self.communicator().stringToProxy(game_proxy[0])
            game_server = IceGauntlet.GamePrx.checkedCast(proxy)
            #print("\nTe has conectado al Proxy: " + gameProxy)

            if not game_server:
                raise RuntimeError('Invalid proxy')

            new_levels = self.get_rooms(game_server, int(cantidad_de_mapas))
            self._levels_ = new_levels
            #print(self._levels_)

        except IceGauntlet.RoomNotExists:
            print("No hay mapas disponibles en el servidor")

    def get_rooms(self, game_server, cantidad_de_mapas):
        '''
        Invokes n times gatRoom() depending on the number selected by the user
        saves them and returns a list with the level names
        '''
        rooms = list()
        for i in range(cantidad_de_mapas):
            room_data = game_server.getRoom()
            rooms.append(self.save_room(room_data))
        return rooms

    def save_room(self, room_data):
        '''Saves a room in the assests folder'''
        room_dict = json.loads(room_data)
        room_name = ""
        for _x in room_dict["room"].split(' '):
            room_name += _x
        room_file = room_name+'.json'
        room_file_path = './src/icegauntlet2/assets/'+room_name+'.json'

        with open(room_file_path, 'w') as roomfile:
            json.dump(room_dict, roomfile, indent=4)

        return room_file

    def generate_dungeon_map(self):
        '''Returns a game.DungeonMap object'''
        return game.DungeonMap(self._levels_)

@atexit.register
# pylint: disable=W0613
def bye(*args, **kwargs):
    '''Exit callback, use for shoutdown'''
    print('Thanks for playing!')
# pylint: enable=W0613

def parse_commandline():
    '''Parse and check commandline'''
    parser = argparse.ArgumentParser('IceDungeon Local Game')
    #parser.add_argument('LEVEL', nargs='+', default=[DEFAULT_ROOM], help='List of levels')
    parser.add_argument("PROXY", help="Proxy del servicio de juego")
    parser.add_argument(
        '-p', '--player', default=DEFAULT_HERO, choices=game.common.HEROES,
        dest='hero', help='Hero to play with'
    )
    options = parser.parse_args()

    #for level_file in options.LEVEL:
        #if not game.assets.search(level_file):
            #logging.error(f'Level "{level_file}" not found!')
            #return None
    return options


def main():
    '''Start game according to commandline'''
    user_options = parse_commandline()
    if not user_options:
        return BAD_COMMAND_LINE

    try:
        game.pyxeltools.initialize()
        remote_dungeon = RemoteDungeonMap()
        arg = list()
        arg.append(user_options.PROXY)
        remote_dungeon.main(arg)
        dungeon = remote_dungeon.generate_dungeon_map()
        gauntlet = game.Game(user_options.hero, dungeon)
        gauntlet.add_state(game.screens.TileScreen, game.common.INITIAL_SCREEN)
        gauntlet.add_state(game.screens.StatsScreen, game.common.STATUS_SCREEN)
        gauntlet.add_state(game.screens.GameScreen, game.common.GAME_SCREEN)
        gauntlet.add_state(game.screens.GameOverScreen, game.common.GAME_OVER_SCREEN)
        gauntlet.add_state(game.screens.GoodEndScreen, game.common.GOOD_END_SCREEN)
        gauntlet.start()
    except IceGauntlet.RoomNotExists:
        return 1

    return EXIT_OK

if __name__ == '__main__':
    sys.exit(main())
