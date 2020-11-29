#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W1203
# pylint: disable=W0613

import sys
import Ice
import json
import argparse
import getpass
import hashlib
from tkinter import Tk
from tkinter.filedialog import askopenfilename
Ice.loadSlice('IceGauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

TOKEN_FILE = 'token.txt'

class MapManClient(Ice.Application):
    def run(self, argv):
        try:
            args = self.parseArgs(argv)
            proxy = self.communicator().stringToProxy(args.Proxy)
            mapManServer = IceGauntlet.MapManagementPrx.checkedCast(proxy)
            print("\nTe has conectado al Proxy: " + args.Proxy)
            
            if not mapManServer:
                raise RuntimeError('Invalid proxy')
            
            self.printMenu(mapManServer)
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
        except Ice.Exception:
            print("Proxy no disponible en este momento\nException: Connection Refused")
            return 4
        except noOptionSelected:
            print("No se ha seleccionado ninguna opcion valida")
            return 5
        except incorrectFile:
            print("El archivo seleccionado no es un archivo JSON")
            return 6
        except invalidMap:
            print("El Mapa seleccionado no es válido")
            return 7
        except KeyError:
            print("El archivo seleccionado no es un Mapa")
            return 8         
        except EOFError:
            return 9
        except RuntimeError:
            return 10
           
    def printMenu(self, mapManServer):
        option = input("\n¿Qué quieres hacer?:\n1.Publicar un Mapa\n2.Borrar un Mapa\n")
        if option == '1':
            token = self.readToken()
            newMapDict = self.readMapJson()
            newMap = json.dumps(newMapDict)

            mapManServer.publish(token, newMap)

        elif option == '2':
            token = self.readToken()
            roomName = input("Introduce el nombre del mapa que quieres eliminar: ")
            
            mapManServer.remove(token, roomName)
        else:
            raise noOptionSelected

    @staticmethod
    def parseArgs(argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("Proxy", help="Aqui va el proxy generado por el Map Manager Server")
        args = parser.parse_args()
        return args
    
    @staticmethod
    def readToken():
        tokenTxt = open(TOKEN_FILE, "r")
        token = tokenTxt.read()
        tokenTxt.close()
        return token
    
    @staticmethod
    def readMapJson():
        Tk().withdraw()
        newMapPath = askopenfilename()
        
        if newMapPath[-4:] == "json":
            newMapFile = open(newMapPath)
            newMapDict = json.load(newMapFile)
        else:
            raise incorrectFile
        
        if not newMapDict["room"]:
            raise invalidMap
        
        return newMapDict 

class customError(Exception):
    pass

class noOptionSelected(customError):
    pass

class incorrectFile(customError):
    pass

class invalidMap(customError):
    pass

sys.exit(MapManClient().main(sys.argv))