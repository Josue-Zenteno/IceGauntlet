#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W0613

'''
   ICE Gauntlet Token Server
'''

import sys
import json
import random
import signal
import string
import logging
import os.path

import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet


USERS_FILE = 'users.json'
PASSWORD_HASH = 'password_hash'
CURRENT_TOKEN = 'current_token'
TOKEN_SIZE = 40


def _build_token_():
    valid_chars = string.digits + string.ascii_letters
    return ''.join([random.choice(valid_chars) for _ in range(TOKEN_SIZE)])


class AuthenticationI(IceGauntlet.Authentication):
    '''Authentication servant'''
    def __init__(self):
        self._users_ = {}
        self._active_tokens_ = set()
        if os.path.exists(USERS_FILE):
            self.refresh()
        else:
            self.__commit__()

    def refresh(self, *args, **kwargs):
        '''Reload user DB to RAM'''
        logging.debug('Reloading user database')
        with open(USERS_FILE, 'r') as contents:
            self._users_ = json.load(contents)
        self._active_tokens_ = set([
            user.get(CURRENT_TOKEN, None) for user in self._users_.values()
        ])

    def __commit__(self):
        logging.debug('User database updated!')
        with open(USERS_FILE, 'w') as contents:
            json.dump(self._users_, contents, indent=4, sort_keys=True)

    def changePassword(self, user, currentPassHash, newPassHash, current=None):
        '''Set/Change user password'''
        logging.debug(f'Change password requested by {user}')
        if user not in self._users_:
            raise IceGauntlet.Unauthorized()
        current_hash = self._users_[user].get(PASSWORD_HASH, None)
        if current_hash is None:
            # User auth is empty
            self._users_[user][CURRENT_TOKEN] = _build_token_()
        else:
            if current_hash != currentPassHash:
                raise IceGauntlet.Unauthorized()
        self._users_[user][PASSWORD_HASH] = newPassHash
        self.__commit__()

    def getNewToken(self, user, passwordHash, current=None):
        '''Create new auth token'''
        logging.debug(f'New token requested by {user}')
        if user not in self._users_:
            raise IceGauntlet.Unauthorized()
        current_hash = self._users_[user].get(PASSWORD_HASH, None)
        if not current_hash:
            # User auth is empty
            raise IceGauntlet.Unauthorized()
        if current_hash != passwordHash:
            raise IceGauntlet.Unauthorized()

        current_token = self._users_[user].get(CURRENT_TOKEN, None)
        if current_token:
            # pylint: disable=W0702
            try:
                self._active_tokens_.remove(current_token)
            except:
                # Token is already inactive!
                pass
            # pylint: enable=W0702
        new_token = _build_token_()
        self._users_[user][CURRENT_TOKEN] = new_token
        self.__commit__()
        self._active_tokens_.add(new_token)
        return new_token

    def getOwner(self, token, current=None):
        '''Return if token is active'''
        if token not in self._active_tokens_:
            raise IceGauntlet.Unauthorized

        for user_name in self._users_:
            if self._users_[user_name][CURRENT_TOKEN] == token:
                return user_name

class Server(Ice.Application):
    '''
    Authentication Server
    '''
    def run(self, args):
        '''
        Server loop
        '''
        logging.debug('Initializing server...')
        servant = AuthenticationI()
        signal.signal(signal.SIGUSR1, servant.refresh)

        adapter = self.communicator().createObjectAdapter('AuthenticationAdapter')
        proxy = adapter.add(servant, self.communicator().stringToIdentity('default'))
        adapter.addDefaultServant(servant, '')
        adapter.activate()
        logging.debug('Adapter ready, servant proxy: {}'.format(proxy))
        print('"{}"'.format(proxy), flush=True)

        logging.debug('Entering server loop...')
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
