#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

'''
Shortcut to search for assets files
'''

import os.path


_FOLDERS_PATH_ = [
    'src/icegauntlet2/assets',
    '$HOME/.icegauntlet2/assets',
    '/usr/local/share/src/icegauntlet2/assets',
    '/usr/share/src/icegauntlet2/assets'
]

def search(filename):
    '''Search for given filename in assets folder and return if found'''
    if os.path.exists(filename):
        return filename

    for candidate in _FOLDERS_PATH_:
        candidate = os.path.join(os.path.expandvars(os.path.expanduser(candidate)), filename)
        if os.path.exists(candidate):
            return candidate

    return None
