#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W1203
# pylint: disable=W0613

import sys
import Ice
import argparse
import getpass
import hashlib
Ice.loadSlice('IceGauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

class AuthClient(Ice.Application):
    def run(self, argv):
        try:
            args = self.parseArgs(argv)

            proxy = self.communicator().stringToProxy(args.Proxy)
            authServer = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
            print("\nTe has conectado al Proxy: " + args.Proxy + "\n(Si es la primera vez que accedes, debes obtener primero una contraseña)")
            
            if not authServer:
                raise RuntimeError('Invalid proxy')
            
            if args.Token:
                self.printMenu(authServer, args.User, 1)
            if args.Password:
                self.printMenu(authServer, args.User, 2)
        except IceGauntlet.Unauthorized:
            print("Usuario y/o Contraseña no válida")
            sys.exit(1)
        except Ice.Exception:
            print("Proxy no disponible en este momento\nException: Connection Refused")
            sys.exit(2)
        except noOptionSelected:
            print("No se ha seleccionado ninguna opción válida")
            sys.exit(3)
        except EOFError:
            sys.exit(4)
        except RuntimeError:
            sys.exit(5)
            
    def printMenu(self, authServer, user, option):
        if option == 1:
            currentPass = getpass.getpass('Password:')
            passwordHash = self.hashPassStr(currentPass)
            
            token = authServer.getNewToken(user, passwordHash)
            print(token)
            self.saveToken(token)

        elif option == 2:
            currentPass = getpass.getpass(prompt="Introduce tu Contraseña actual:")
            currentPassHash = self.hashPassStr(currentPass)
            newPass = getpass.getpass(prompt="Introduce Contraseña nueva:")
            newPassHash = self.hashPassStr(newPass)

            authServer.changePassword(user, currentPassHash, newPassHash)
        else:
            raise noOptionSelected

    @staticmethod
    def hashPassStr(password):
        passwordHasher = hashlib.sha256()
        passwordHasher.update(password.encode())
        passwordHash = passwordHasher.digest()
        return str(passwordHash)

    @staticmethod
    def parseArgs(argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("User", help="Aqui va el nombre de usuario")
        parser.add_argument("Proxy", help="Aqui va el proxy generado por el Athentication Server")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-t", "--Token" , action="store_true",help='Opcion para pedir un nuevo token')
        group.add_argument("-p", "--Password", action="store_true", help='Opcion para cambiar contraseña')
        args = parser.parse_args()
        return args
    
    @staticmethod
    def saveToken(token):
        tokenTxt = open("token.txt", "w")
        tokenTxt.write(token)
        tokenTxt.close()
        print("También se ha guardado en el archivo token.txt")

class customError(Exception):
    pass

class noOptionSelected(customError):
    pass

sys.exit(AuthClient().main(sys.argv))
