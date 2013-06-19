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

from webapp import KeyExists
import metadata

import mapscript
import os.path

def create_mapfile(path, map_name, data):
    if os.path.exists("%s.map" % path):
        raise KeyExists(map_name)

    mf = mapscript.mapObj()
    mf.name = map_name
    
    # The following could be defined in <mapfile.py>:

    mf.web.metadata.set("ows_name", map_name)
    mf.web.metadata.set("ows_title", data.get("title", map_name))
    mf.web.metadata.set("ows_abstract", data.get("abstract", ""))

    # Set default values:
    # It should be configurable to the future.

    # mf.web.metadata.set("ows_keywordlist", "")
    # mf.web.metadata.set("ows_keywordlist_vocabulary", "")
    # + ows_keywordlist_[vocabulary’s name]_items
    # mf.web.metadata.set("wms_onlineresource", "")
    # mf.web.metadata.set("wfs_onlineresource", "")
    # mf.web.metadata.set("wms_service_onlineresource", "")
    # mf.web.metadata.set("wfs_service_onlineresource", "")
    mf.web.metadata.set("wms_srs", "EPSG:4326")
    mf.web.metadata.set("wfs_srs", "EPSG:4326")
    mf.web.metadata.set("wms_bbox_extended", "true")
    # mf.web.metadata.set("wms_resx", "")
    # mf.web.metadata.set("wms_resy", "")

    mf.web.metadata.set("ows_schemas_location", 
                        "http://schemas.opengeospatial.net")
    mf.web.metadata.set("ows_updatesequence", "foo")
    mf.web.metadata.set("ows_addresstype", "foo")
    mf.web.metadata.set("ows_address", "foo")
    mf.web.metadata.set("ows_city", "foo")
    mf.web.metadata.set("ows_stateorprovince", "foo")
    mf.web.metadata.set("ows_postcode", "foo")
    mf.web.metadata.set("ows_contactperson", "foo")
    mf.web.metadata.set("ows_contactposition", "foo")
    mf.web.metadata.set("ows_contactorganization", "foo")
    mf.web.metadata.set("ows_contactelectronicmailaddress", "foo")
    mf.web.metadata.set("ows_contactfacsimiletelephone", "foo")
    mf.web.metadata.set("ows_contactvoicetelephone", "foo")
    mf.web.metadata.set("wms_fees", "none")
    mf.web.metadata.set("wfs_fees", "none")
    mf.web.metadata.set("wms_accessconstraints", "none")
    mf.web.metadata.set("wfs_accessconstraints", "none")
    # mf.web.metadata.set("ows_attribution_logourl_format", "")
    # mf.web.metadata.set("ows_attribution_logourl_height", "")
    # mf.web.metadata.set("ows_attribution_logourl_href", "")
    # mf.web.metadata.set("ows_attribution_logourl_width", "")
    # mf.web.metadata.set("ows_attribution_onlineresource", "")
    # mf.web.metadata.set("ows_attribution_title", "")

    mf.web.metadata.set("wms_enable_request", 
                        "GetCapabilities GetMap GetFeatureInfo GetLegendGraphic")
    mf.web.metadata.set("wfs_enable_request", 
                        "GetCapabilities DescribeFeatureType GetFeature")
    mf.web.metadata.set("ows_sld_enabled", "true")
    mf.web.metadata.set("wms_getcapabilities_version", "1.3.0")
    mf.web.metadata.set("wfs_getcapabilities_version", "1.0.0")
    # mf.web.metadata.set("wms_getmap_formatlist", "")
    # mf.web.metadata.set("wms_getlegendgraphic_formatlist", "")
    mf.web.metadata.set("wms_feature_info_mime_type",
                        "application/vnd.ogc.gml,text/plain")
                        # TODO: text/html
    mf.web.metadata.set("wms_encoding", "UTF-8")
    mf.web.metadata.set("wfs_encoding", "UTF-8")

    # mf.web.metadata.set("wms_timeformat", "")
    # mf.web.metadata.set("wms_languages", "")
    # mf.web.metadata.set("wms_layerlimit", "")
    # mf.web.metadata.set("wms_rootlayer_abstract", "")
    # mf.web.metadata.set("wms_rootlayer_keywordlist", "")
    # mf.web.metadata.set("wms_rootlayer_title", "")
    # mf.web.metadata.set("wfs_maxfeatures", "")
    # mf.web.metadata.set("wfs_feature_collection", "")
    # mf.web.metadata.set("wfs_namespace_uri", "")
    # mf.web.metadata.set("wfs_namespace_prefix", "")

    mf.status = mapscript.MS_ON
    mf.setSize(256,256)
    mf.maxsize = 4096
    mf.resolution = 96
    mf.imagetype = 'png'
    mf.imagecolor.setRGB(255,255,255)
    mf.setProjection("init=epsg:4326")
    mf.setExtent(-180,-90,180,90)
    mf.units = mapscript.MS_DD

    mf.save("%s.map" % path)
