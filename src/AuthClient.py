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
            
            self.printMenu(authServer)
            return 0
        except IceGauntlet.Unauthorized:
            print("Usuario y/o Contraseña no válida")
            return 1
        except Ice.Exception:
            print("Proxy no disponible en este momento\nException: Connection Refused")
            return 2
        except noOptionSelected:
            print("No se ha seleccionado ninguna opción válida")
            return 3
        except EOFError:
            return 4
        except RuntimeError:
            return 5
            
    def printMenu(self, authServer):
        option = input("\n¿Qué quieres hacer?:\n1.Obtener token de autorización\n2.Cambiar contraseña\n")
        if option == '1':
            user = input("Introduce tu Usuario: ")
            currentPass = getpass.getpass(prompt="Introduce tu Contraseña:")
            passwordHash = self.hashPassStr(currentPass)
            
            token = authServer.getNewToken(user, passwordHash)
            self.saveToken(token)

        elif option == '2':
            user = input("Introduce tu Usuario: ")
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
        parser.add_argument("Proxy", help="Aqui va el proxy generado por el Athentication Server")
        args = parser.parse_args()
        return args
    
    @staticmethod
    def saveToken(token):
        tokenTxt = open("token.txt", "w")
        tokenTxt.write(token)
        tokenTxt.close()
        print("Tu token de identificación es: "+token+"\nTambién se ha guardado en el archivo token.txt")

class customError(Exception):
    pass

class noOptionSelected(customError):
    pass

sys.exit(AuthClient().main(sys.argv))
