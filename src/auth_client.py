#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W0613

'''
    ICE Gauntlet Authentication Client
'''

import sys
import argparse
import getpass
import hashlib

import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet


class AuthClient(Ice.Application):
    '''Authentication client'''
    def run(self, argv):
        try:
            args = self.parse_args(argv)

            proxy = self.communicator().stringToProxy(args.Proxy)

            auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy)

            if not auth_server:
                raise RuntimeError('Invalid proxy')

            if args.Token:
                self.obtain_token(auth_server, args.User)

            if args.Password:
                self.update_password(auth_server, args.User)

            return 0
        except IceGauntlet.Unauthorized:
            print("Usuario y/o Contraseña no válida")
            return 1
        except Ice.Exception:
            print("Proxy no disponible en este momento\nException: Connection Refused")
            return 2
        except EOFError:
            return 3
        except RuntimeError:
            return 4
        except SystemExit:
            return 5

    def obtain_token(self, auth_server, user):
        '''Ask for the password and invokes getNewToken()'''
        current_pass = getpass.getpass('Password:')
        password_hash = self.hash_pass_str(current_pass)

        token = auth_server.getNewToken(user, password_hash)
        print(token)
        self.save_token(token)

    def update_password(self, auth_server, user):
        '''Ask for both current and new passwords then invokes changePassword()'''
        current_pass = getpass.getpass(prompt="Introduce tu Contraseña actual:")

        if current_pass != "":
            current_pass_hash = self.hash_pass_str(current_pass)
        else:
            current_pass_hash = None

        new_pass = getpass.getpass(prompt="Introduce Contraseña nueva:")
        new_pass_hash = self.hash_pass_str(new_pass)

        auth_server.changePassword(user, current_pass_hash, new_pass_hash)

    @staticmethod
    def hash_pass_str(password):
        '''Hashes a password'''
        password_hasher = hashlib.sha256()
        password_hasher.update(password.encode())
        password_hash = password_hasher.digest()
        return str(password_hash)

    @staticmethod
    def parse_args(argv):
        '''Parse the arguments'''
        parser = argparse.ArgumentParser()
        parser.add_argument("User", help="Aqui va el nombre de usuario")
        parser.add_argument("Proxy", help="Aqui va el proxy generado por el Athentication Server")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-t", "--Token", action="store_true", help='Pedir un nuevo token')
        group.add_argument("-p", "--Password", action="store_true", help='Cambiar contraseña')
        args = parser.parse_args()
        return args

    @staticmethod
    def save_token(token):
        '''Saves the obtained token in a txt file'''
        token_txt = open("token.txt", "w")
        token_txt.write(token)
        token_txt.close()
        print("También se ha guardado en el archivo token.txt")

sys.exit(AuthClient().main(sys.argv))
