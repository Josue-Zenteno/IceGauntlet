#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W0613

'''
    Map Client
'''

import sys
import json
import argparse

import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

class MapManClient(Ice.Application):
    '''Map Client'''
    def run(self, argv):
        try:
            args = self.parse_args(argv)
            proxy = self.communicator().stringToProxy(args.Proxy)
            map_man_server = IceGauntlet.RoomManagerPrx.checkedCast(proxy)
            #print("\nTe has conectado al Proxy: " + args.Proxy)

            if not map_man_server:
                raise RuntimeError('Invalid proxy')

            if args.newMapPath:
                self.publish_map(map_man_server, args.Token, args.newMapPath)

            if args.roomName:
                self.remove_map(map_man_server, args.Token, args.roomName)

            return 0
        except IceGauntlet.Unauthorized:
            print("Usuario y/o Contraseña no válida")
            return 1
        except IceGauntlet.RoomAlreadyExists:
            print("Ya existe un mapa con ese nombre y es de otro usuario")
            return 2
        except IceGauntlet.RoomNotExists:
            print("El mapa que estas intentando borrar no existe o es de otra persona")
            return 3
        except IceGauntlet.WrongRoomFormat:
            print("El archivo introducido no es un mapa valido")
        except Ice.Exception:
            print("Proxy no disponible en este momento\nException: Connection Refused")
            return 4
        except IncorrectFile:
            print("El archivo seleccionado no es un archivo JSON")
            return 5
        except EOFError:
            return 6
        except RuntimeError:
            return 7
        except SystemExit:
            return 8

    def publish_map(self, map_man_server, token, new_map_path):
        '''Sends new room data as string invoking publish()'''
        new_map_dict = self.read_map_json(new_map_path)
        new_map = json.dumps(new_map_dict)
        map_man_server.publish(token, new_map)

    def remove_map(self, map_man_server, token, room_name):
        '''Invokes remove()'''
        map_man_server.remove(token, room_name)

    @staticmethod
    def parse_args(argv):
        '''Parse the arguments'''
        parser = argparse.ArgumentParser()
        parser.add_argument("Proxy", help="Aqui va el proxy generado por el Map Server")
        parser.add_argument("Token", help="Aqui va el token obtenido del Authentication Server")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-p", "--Publish", dest="newMapPath", help="Opcion para publicar mapa")
        group.add_argument("-r", "--Remove", dest="roomName", help="Opcion para borrar mapa")

        args = parser.parse_args()

        return args

    @staticmethod
    def read_map_json(new_map_path):
        '''Checks if the path leads to a json file and then turn it into a dictorinary'''
        if new_map_path[-4:] != "json":
            raise IncorrectFile

        new_map_file = open(new_map_path)
        new_map_dict = json.load(new_map_file)

        return new_map_dict

class CustomError(Exception):
    '''Custom Error Exception'''

class IncorrectFile(CustomError):
    '''Custom Error Exception'''

sys.exit(MapManClient().main(sys.argv))
