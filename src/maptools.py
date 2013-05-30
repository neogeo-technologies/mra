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

import mapscript

def create_def_polygon_class(layer, s_name='default_polygon'):
    layer.classgroup = s_name
    class0 = mapscript.classObj(layer)
    class0.name = 'Class given in default'
    class0.group = s_name
    style0 = mapscript.styleObj(class0)
    style0.width = 1
    style0.color = mapscript.colorObj(220, 220, 220)
    style0.outlinecolor = mapscript.colorObj(96, 96, 96)


def create_def_line_class(layer, s_name='default_line'):
    layer.classgroup = s_name
    class0 = mapscript.classObj(layer)
    class0.name = 'Class given in default'
    class0.group = s_name
    style0 = mapscript.styleObj(class0)
    style0.width = 2
    style0.color = mapscript.colorObj(96, 96, 96)


def create_def_point_class(layer, s_name='default_point'):
    layer.classgroup = s_name
    class0 = mapscript.classObj(layer)
    class0.name = 'Class given in default'
    class0.group = s_name
    style0 = mapscript.styleObj(class0)
    style0.size = 8
    style0.color = mapscript.colorObj(96, 96, 96)

