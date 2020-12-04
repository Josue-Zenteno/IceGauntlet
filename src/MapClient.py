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

class MapManClient(Ice.Application):
    def run(self, argv):
        try:
            args = self.parseArgs(argv)
            proxy = self.communicator().stringToProxy(args.Proxy)
            mapManServer = IceGauntlet.MapManagementPrx.checkedCast(proxy)
            #print("\nTe has conectado al Proxy: " + args.Proxy)
            
            if not mapManServer:
                raise RuntimeError('Invalid proxy')
            
            if args.newMapPath:
                self.publishMap(mapManServer, args.Token, args.newMapPath)
            
            if args.roomName:
                self.removeMap(mapManServer, args.Token, args.roomName)

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
        except incorrectFile:
            print("El archivo seleccionado no es un archivo JSON")
            return 5        
        except EOFError:
            return 6
        except RuntimeError:
            return 7
           
    def publishMap(self, mapManServer, token, newMapPath):
        newMapDict = self.readMapJson(newMapPath)
        newMap = json.dumps(newMapDict)
        mapManServer.publish(token, newMap)

    def removeMap(self, mapManServer, token, roomName):
        mapManServer.remove(token, roomName)

    @staticmethod
    def parseArgs(argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("Proxy", help="Aqui va el proxy generado por el Map Server")
        parser.add_argument("Token", help="Aqui va el token obtenido del Authentication Server")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-p", "--Publish" , dest="newMapPath",help="Opcion para publicar mapa")
        group.add_argument("-r", "--Remove", dest="roomName", help="Opcion para borrar mapa")
        
        args = parser.parse_args()
        
        return args
    
    @staticmethod
    def readMapJson(newMapPath):

        if newMapPath[-4:] != "json":
            raise incorrectFile

        newMapFile = open(newMapPath)
        newMapDict = json.load(newMapFile)

        return newMapDict 

class customError(Exception):
    pass

class incorrectFile(customError):
    pass

sys.exit(MapManClient().main(sys.argv))
