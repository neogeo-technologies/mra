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

import mapfile
import pyxml

import webapp

import xml.etree.ElementTree as etree
from osgeo import osr

__config = None

def get_config(key=None, mode='r'):
    """This reads the YAML configuration file."""

    global __config
    if not __config:
        try:
            __config = yaml.load(open(os.path.join(sys.path[0], 'mra.yaml'), mode))
        except yaml.YAMLError, exc:
            exit('Error in configuration file: %s' % exc)
    return __config if key == None else __config[key] if key in __config else {}

def get_mapfile_paths():
    """Generates a list of mapfile paths managed by Mapserver REST API."""

    for (root, subFolders, files) in os.walk(get_config('storage')['mapfiles']):
        for f in files:
            if f.endswith('.map') and not f.startswith('.'):
                yield os.path.join(root, f)

def get_mapfile(name):
    with webapp.mightNotFound(message="Could not find mapfile '%s'." % name, exceptions=(IOError, OSError, KeyError)):
        mf = mapfile.Mapfile(name, get_config('storage')['mapfiles'])
    return mf

def get_mapfile_workspace(mf_name, ws_name):
    mf = get_mapfile(mf_name)
    with webapp.mightNotFound("workspace", mapfile=mf_name):
        ws = mf.get_workspace(ws_name)
    return mf, ws

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

def get_resource_path(*args):
    return safe_path_join(get_config('storage')['resources'], *args)

def get_st_data_path(ws_name, st_type, name, *args):
    return get_resource_path("workspaces", ws_name, st_type, name, *args)

def get_ds_data_path(ws_name, name, *args):
    return get_st_data_path(ws_name, "datastores", name, *args)

def get_cs_data_path(ws_name, name, *args):
    return get_st_data_path(ws_name, "coveragestores", name, *args)

def get_style_path(name, *args):
    return safe_path_join(get_config('storage')['resources'], "styles", name, *args)

def iter_styles(mapfile=None):
    """Generates a list of style paths managed by Mapserver REST API."""

    used_styles = list(mapfile.iter_styles()) if mapfile else []

    for s in used_styles:
        yield s

    styles_dir = os.path.join(get_config('storage')['resources'], "styles")
    if not os.path.isdir(styles_dir):
        return

    for (root, subFolders, files) in os.walk(styles_dir):
        for f in files:
            if f not in used_styles:
                yield f


def mk_path(path):
    dirs = os.path.dirname(path)
    if not os.path.isdir(dirs):
        os.makedirs(dirs)

def mk_ds_data_path(ws_name, name, *args):
    path = get_dws_data_path(name, *args)
    mk_path(path)
    return path

def mk_cs_data_path(ws_name, name, *args):
    path = get_cs_data_path(ws_name, name, *args)
    mk_path(path)
    return path

def mk_st_data_path(ws_name, st_type, name, *args):
    path = get_st_data_path(ws_name, st_type, name, *args)
    mk_path(path)
    return path

def mk_style_path(name, *args):
    path = get_style_path(name, *args)
    mk_path(path)
    return path

def no_root(root, path):
    path = os.path.abspath(path)
    root = os.path.abspath(root)
    return path[len(root):] if path.startswith(root) else path

def no_res_root(path):
    return os.path.relpath(path, get_config('storage')['resources'])

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
    
    if srs.GetAuthorityCode('PROJCS') == None and srs.GetAuthorityCode('GEOGCS') != None :
        return srs.GetAuthorityName('GEOGCS'), srs.GetAuthorityCode('GEOGCS')
    if srs.GetAuthorityCode('PROJCS') != None:
        return srs.GetAuthorityName('PROJCS'), srs.GetAuthorityCode('PROJCS')
    else:
        raise KeyError("Unable to get authority from %s" % wkt)

