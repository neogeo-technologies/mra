#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                       #
#   MapServer REST API is a python wrapper around MapServer which       #
#   allows to manipulate a mapfile in a RESTFul way. It has been        #
#   developped to match as close as possible the way the GeoServer      #
#   REST API acts.                                                      #
#                                                                       #
#   Copyright (C) 2011-2013 Neogeo Technologies.                        #
#                                                                       #
#   This file is part of MapServer Rest API.                            #
#                                                                       #
#   MapServer Rest API is free software: you can redistribute it        #
#   and/or modify it under the terms of the GNU General Public License  #
#   as published by the Free Software Foundation, either version 3 of   #
#   the License, or (at your option) any later version.                 #
#                                                                       #
#   MapServer Rest API is distributed in the hope that it will be       #
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the     #
#   GNU General Public License for more details.                        #
#                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

"""
    Module for managing add-ons (experimental).

"""

import sys
import os.path
import logging

class ExtensionManager(object):

    def __init__(self, ):
        self.extentions = {}

    def load_plugins(self, pkg_name):
        sys.path.append(__file__)
        __import__(pkg_name, globals(), locals(), ["*"])
        sys.path.remove(__file__)

    def load_plugins_dir(self, dir_path):
        path, pkg = os.path.split(os.path.abspath(dir_path))
        pkg, _ = os.path.splitext(pkg)
        print "Loading %s from %s" % (pkg, path)

        sys.path.append(path)
        try:
            self.load_plugins(pkg)
        except ImportError:
            logging.error("Could not load plugin package \"%s\" from %s" % (pkg, path))
        else:
            logging.info("Loaded plugin package \"%s\" from %s" % (pkg, path))
        sys.path.remove(path)

    def extend(self, name, *args, **kwargs):
        for f in self.extentions.get(name, []):
            f(*args, **kwargs)

    def register(self, name, f=None):
        if f == None:
            def decorator(f):
                self.register(name, f)
                return f
            return decorator

        self.extentions.setdefault(name, []).append(f)

plugins = ExtensionManager()
