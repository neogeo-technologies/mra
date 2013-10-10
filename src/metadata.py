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
    Wrapper for managing metadata of mapfiles.

    MRA requires the use of its own metadata, which appear as "mra" in mapfiles.
    This module is to simplify their use.

"""

import yaml
import contextlib
from mapscript import MapServerError

METADATA_NAME="mra"

def get_metadata(obj, key, *args):
    """Returns Metadata for a mapObj or a layerObj.
    get_metadata(obj, key, [default]) -> value

    """
    if len(args) > 1:
        return TypeError("get_metadata expected at most 3 arguments, got %d" % (2 + len(args)))

    try:
        value = obj.getMetaData(key)
    # We never now what mapscript might throws at us...
    except MapServerError:
        value = None

    if value == None:
        if not args:
            raise KeyError(key)
        value = args[0]

    if isinstance(value, basestring):
        value = value.encode("UTF8")

    return value

def iter_metadata_keys(obj):
    # Prepare for ugliness...

    keys = []
    key = obj.getFirstMetaDataKey()
    while key != None:
        keys.append(key)
        key = obj.getNextMetaDataKey(key)

    return keys

def get_metadata_keys(obj):
    return list(iter_metadata_keys(obj))

def set_metadata(obj, key, value):
    obj.setMetaData(key, value)

def set_metadatas(obj, metadatas):
    # TODO: erease all metadata first.
    for key, value in metadatas.iteritems():
        set_metadata(obj, key, value)

def update_metadatas(obj, metadatas):
    for key, value in metadatas.iteritems():
        set_metadata(obj, key, value)

def del_metadata(obj, key):
    obj.removeMetaData(key)

@contextlib.contextmanager
def metadata(obj, key, *args):
    """Context manager that exposes the metadata and saves it again.
    Warning: This is only usefull if the metadata is mutable!

    """
    metadata = get_metadata(obj, key, *args)
    yield metadata
    set_metadata(obj, key, metadata)

def __get_mra(obj):
    text = get_metadata(obj, METADATA_NAME, None)
    if text is None:
        return {}

    try:
        metadata = yaml.load(text)
    except yaml.parser.ParserError:
        raise IOError("File has corrupted MRA metadata for entry \"%s\"." % key)
    return metadata

def __save_mra(obj, mra_metadata):
    set_metadata(obj, METADATA_NAME, yaml.safe_dump(mra_metadata))

def get_mra_metadata(obj, key, *args):
    """get_metadata(obj, key, [default]) -> value"""

    if len(args) > 1:
        return TypeError("get_mra_metadata expected at most 3 arguments, got %d" % (2 + len(args)))

    mra_metadata = __get_mra(obj)

    try:
        return mra_metadata[key]
    except KeyError:
        if not args:
            raise
        return args[0]

def iter_mra_metadata_keys(obj):
    return __get_mra(obj).iterkeys()

def get_mra_metadata_keys(obj):
    return __get_mra(obj).keys()

def update_mra_metadatas(obj, update):
    with mra_metadata(obj) as metadata:
        metadata.update(update)

def set_mra_metadatas(obj, mra_metadata):
    __save_mra(obj, mra_metadata)

def set_mra_metadata(obj, key, value):
    with mra_metadata(obj) as metadata:
        metadata[key] = value

def del_mra_metadata(obj, key, value):
    with mra_metadata(obj) as mra_metadata:
        del metadata[key]

@contextlib.contextmanager
def mra_metadata(obj, *args):
    """Context manager that exposes the mra_metadata and saves it again.
    Warning: This is only usefull if the metadata is mutable!
    If no key is provided the metadata dict itobj is exposed.
    Usage: with mra_metadata(obj, [key, [dflt, setdefault] ]) as metadata

    """
    if not args:
        mra_metadata = __get_mra(obj)
        yield mra_metadata
        set_mra_metadatas(obj, mra_metadata)
    else:
        metadata = get_mra_metadata(obj, *args)
        yield metadata
        set_mra_metadata(obj, args[0], metadata)
