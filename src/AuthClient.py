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

class Client(Ice.Application):
    def run(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("Proxy", help="Aqui va el proxy generado por el server")
        args = parser.parse_args()

        proxy = self.communicator().stringToProxy(args.Proxy)
        print(args.Proxy)
        authServer = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        
        if not authServer:
            raise RuntimeError('Invalid proxy')
        
        self.printMenu(authServer)

        return 0

        
    def printMenu(self, authServer):
        option = input("Select an option: \n1.Obtener token de autorización\n2.Cambiar contraseña\n")
        if option == '1':
            user = input("Introduce tu nombre: ")
            password = getpass.getpass(prompt="Introduce contraseña:")
            passwordHash = hashlib.sha256()
            passwordHash.update(password.encode())
            token = authServer.getNewToken(user, passwordHash.digest().decode())
            print(token)
            

        if option == '2':
            user = input("Introduce tu nombre: ")
            currentPass = getpass.getpass(prompt="Introduce contraseña:")
            if currentPass == "":
                password = None
            else:
                currentPassHash = hashlib.sha256()
                currentPassHash.update(currentPass.encode())
                password = currentPassHash.digest().decode()
                
            newPass = getpass.getpass(prompt="Introduce contraseña nueva:")
            newPassHash = hashlib.sha256()
            newPassHash.update(newPass.encode())
            authServer.changePassword(user, password, newPassHash.digest().decode())


sys.exit(Client().main(sys.argv))