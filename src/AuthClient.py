#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W1203
# pylint: disable=W0613

import sys
import Ice
import argparse
Ice.loadSlice('IceGauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        print(argv[1])
        authServer = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        
        if not authServer:
            raise RuntimeError('Invalid proxy')
        
        self.printMenu()

        
    def printMenu(self):
        pass