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

import os
import yaml
import sys

import pyxml

import webapp

import xml.etree.ElementTree as etree
from osgeo import osr

__config = None

def assert_is_empty(generator, tname, iname):
    try:
        next(generator)
    except StopIteration:
        pass # Everything is ok.
    else:
        raise webapp.Forbidden(message="Can't remove '%s' because it is an non-empty %s." % (iname, tname))

def href(url):
    return pyxml.Entries({'href': url})

def safe_path_join(root, *args):
    full_path = os.path.realpath(os.path.join(root, *args))
    if not full_path.startswith(os.path.realpath(root)):
        raise webapp.Forbidden(message="path '%s' outside root directory." % (args))
    return full_path

def is_hidden(path):
    # TODO Add a lot of checks, recursive option (to check folders)
    # MacOSX has at least four ways to hide files...
    return os.path.basename(path).startswith(".")

def wkt_to_proj4(wkt):
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    return srs.ExportToProj4()

def proj4_to_wkt(proj4):
    srs = osr.SpatialReference()
    srs.ImportFromProj4(proj4)
    return srs.ExportToWkt()

def wkt_to_authority(wkt):
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)

    # Are there really no other with osgeo? Oo

    if srs.GetAuthorityCode('PROJCS') != None:
        return srs.GetAuthorityName('PROJCS'), srs.GetAuthorityCode('PROJCS')
    elif srs.GetAuthorityCode('GEOGCS') != None :
        return srs.GetAuthorityName('GEOGCS'), srs.GetAuthorityCode('GEOGCS')
    else:
        return "Unknown", "Unknown"
