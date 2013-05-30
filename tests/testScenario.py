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

from utils import APIRequest

import sys

def testScenario():

    target = "http://192.168.1.39/mra/"
    map_name = "test"


    # GET workspaces.

    wss = APIRequest("GET", target + "/maps/test/workspaces")["workspaces"]
    assert len(wss) == 1
    assert wss[0]["name"] == "default"

    # GET workspaceName

    ws = APIRequest("GET", wss[0]["href"])["workspace"]
    assert ws["name"] == wss[0]["name"]

    # GET dataStores

    dss = APIRequest("GET", ws["dataStores"]["href"])["dataStores"]

    # DELETE the dataStores

    for ds in dss:
        APIRequest("DELETE", ds["href"])

    # POST a datastore and GET it

    name, title = "testDS1", "test datastore 1"
    _, r = APIRequest("POST", ws["dataStores"]["href"], {"dataStore":{"name":name, "title":title}},
                      get_response=True)
    ds_link = r.getheader("Location")

    ds = APIRequest("GET", ds_link)["dataStore"]
    assert ds["name"] == name
    assert ds["title"] == title

    # PUT a datastore

    ds["title"] = title.upper()
    del ds["href"]
    APIRequest("PUT", ds_link, {"dataStore":ds})

    ds = APIRequest("GET", ds_link)["dataStore"]
    assert ds["title"] == title.upper()

    # GET featuretypes

    fts = APIRequest("GET", ds["href"])["featureTypes"]
    assert len(fts) == 0


    # PUT file

    APIRequest("PUT", ds_link + "/file.shp", open("./files/timezones_shp.zip", "rb"),
               encode=None, content_type="application/zip")

    ds = APIRequest("GET", ds_link)["dataStore"]
    assert ds["connectionParameters"]["path"] = "workspaces/%s/datastores/%s/timezones.shp" % (
        ws["name"], ds["name"])

