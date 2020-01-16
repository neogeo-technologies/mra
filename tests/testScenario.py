# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                       #
#   MapServer REST API is a python wrapper around MapServer which       #
#   allows to manipulate a mapfile in a RESTFul way. It has been        #
#   developped to match as close as possible the way the GeoServer      #
#   REST API acts.                                                      #
#                                                                       #
#   Copyright (C) 2011-2020 Neogeo Technologies.                        #
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

import utils
from utils import APIRequest

import sys
import random

def _test_workspaces(target, map_name, delete=True):

    # GET workspaces.

    wss = APIRequest("GET", target + "/maps/" + map_name + "/workspaces")["workspaces"]
    assert len(wss) == 1
    assert wss[0]["name"] == "default"

    # GET workspaceName

    ws = APIRequest("GET", wss[0]["href"])["workspace"]
    assert ws["name"] == wss[0]["name"]

    #
    # Test DataStores.
    #

    # GET dataStores

    dss = APIRequest("GET", ws["dataStores"]["href"])["dataStores"]
    assert len(dss) == 0

    # POST a datastore and GET it

    name, title = "testDS1", "test datastore 1"
    _, r = APIRequest("POST", ws["dataStores"]["href"], {"dataStore":{"name":name, "title":title}},
                      get_response=True)
    ds_link = r.getheader("Location").rsplit(".", 1)[0]

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


    # PUT file, and check if datastore is updated.

    APIRequest("PUT", ds_link + "/file.shp", open("./files/timezones_shp.zip", "rb"),
               encode=None, content_type="application/zip")

    ds = APIRequest("GET", ds_link)["dataStore"]
    assert ds["connectionParameters"]["url"] == "file:workspaces/%s/datastores/%s/timezones.shp" % (ws["name"], ds["name"])

    # POST a featuretype and GET it

    name, title = "timezones", "test feature type 1"
    _, r = APIRequest("POST", ds["href"], {"featureType":{"name":name, "title":title}},
                      get_response=True)
    ft_link = r.getheader("Location").rsplit(".", 1)[0]

    ft = APIRequest("GET", ft_link)["featureType"]
    assert ft["name"] == name
    assert ft["title"] == title

    # PUT a featuretype

    ft["title"] = title.upper()
    APIRequest("PUT", ft_link, {"featureType":ft})

    ft = APIRequest("GET", ft_link)["featureType"]
    assert ft["title"] == title.upper()

    # DELETE stuff

    if delete:

        APIRequest("DELETE", ft_link)
        fts = APIRequest("GET", ds_link + "/featuretypes")["featureTypes"]
        assert len(fts) == 0

        APIRequest("DELETE", ds_link)
        dss = APIRequest("GET", ws["dataStores"]["href"])["dataStores"]
        assert len(dss) == 0



    #
    # Test CoverageStores.
    #

    # GET coverageStores

    css = APIRequest("GET", ws["coverageStores"]["href"])["coverageStores"]
    assert len(css) == 0

    # POST a coverageStore and GET it

    name, title = "testCS1", "test coverageStore 1"
    _, r = APIRequest("POST", ws["coverageStores"]["href"], {"coverageStore":{"name":name, "title":title}},
                      get_response=True)
    cs_link = r.getheader("Location").rsplit(".", 1)[0]

    cs = APIRequest("GET", cs_link)["coverageStore"]
    assert cs["name"] == name
    assert cs["title"] == title

    # PUT a coverageStore

    cs["title"] = title.upper()
    del cs["href"]
    APIRequest("PUT", cs_link, {"coverageStore":cs})

    cs = APIRequest("GET", cs_link)["coverageStore"]
    assert cs["title"] == title.upper()

    # GET coverages

    fts = APIRequest("GET", cs["href"])["coverages"]
    assert len(fts) == 0


    # PUT file, and check if coverageStore is updated.

    APIRequest("PUT", cs_link + "/file.tif", open("./files/HYP_LR.zip", "rb"),
               encode=None, content_type="application/zip")

    cs = APIRequest("GET", cs_link)["coverageStore"]
    assert cs["connectionParameters"]["url"] == "file:workspaces/%s/coveragestores/%s/HYP_LR/HYP_LR.tif" % (ws["name"], cs["name"])

    # POST a coverage and GET it

    name, title = "HYP_LR", "test coverage 1"
    _, r = APIRequest("POST", cs["href"], {"coverage":{"name":name, "title":title}},
                      get_response=True)
    c_link = r.getheader("Location").rsplit(".", 1)[0]

    ft = APIRequest("GET", c_link)["coverage"]
    assert ft["name"] == name
    assert ft["title"] == title

    # PUT a coverage

    ft["title"] = title.upper()
    APIRequest("PUT", c_link, {"coverage":ft})

    ft = APIRequest("GET", c_link)["coverage"]
    assert ft["title"] == title.upper()

    # DELETE stuff


    if delete:

        APIRequest("DELETE", c_link)
        fts = APIRequest("GET", cs_link + "/coverages")["coverages"]
        assert len(fts) == 0

        APIRequest("DELETE", cs_link)
        css = APIRequest("GET", ws["coverageStores"]["href"])["coverageStores"]
        assert len(css) == 0


    return ws

def _test_styles(target, map_name):

    # Lets DELETE all the styles.
    styles = APIRequest("GET", target + "/maps/" + map_name + "/styles")["styles"]
    for style in styles:
        if style["name"].startswith("__test_"):
            APIRequest("DELETE", style["href"])
    styles = APIRequest("GET", target + "/maps/" + map_name + "/styles")["styles"]
    assert len([style for style in styles if style["name"].startswith("__test_")]) == 0

    # Lets POST a style and GET it.
    name = "__test_awesome_style_name"
    data = open("./files/style.sld").read()
    noise = "".join(map(str, random.sample(xrange(10000000), 60)))
    # We add some noise, so we can check PUT later.

    styles = APIRequest("POST", target + "/maps/" + map_name + "/styles?name=" + name,
                        encode=None, content_type="application/vnd.ogc.sld+xml", data=data+noise)

    styles = APIRequest("GET", target + "/maps/" + map_name + "/styles")["styles"]
    assert len(styles) == 1
    assert styles[0]["name"] == name

    st_link = styles[0]["href"].rsplit(".", 1)[0]
    style = APIRequest("GET", st_link)

    content = APIRequest("GET", style["href"], encode=None, decode=None)
    assert content == data+noise

    # Use PUT to remove the noise in the file.
    styles = APIRequest("PUT", style["href"], encode=None, content_type="application/vnd.ogc.sld+xml", data=data)
    content = APIRequest("GET", style["href"], encode=None, decode=None)
    assert content == data


def _test_layers(target, map_name):
    # We need to setup something to work with first.

    # GET workspaces.
    wss = APIRequest("GET", target + "/maps/" + map_name + "/workspaces")["workspaces"]
    ws = APIRequest("GET", wss[0]["href"])["workspace"]
    # DataStores.
    name, title = "testDS1", "test datastore 1"
    _, r = APIRequest("POST", ws["dataStores"]["href"], {"dataStore":{"name":name, "title":title}},
                      get_response=True)
    ds_link = r.getheader("Location").rsplit(".", 1)[0]
    # PUT file
    APIRequest("PUT", ds_link + "/file.shp", open("./files/timezones_shp.zip", "rb"),
               encode=None, content_type="application/zip")
    ds = APIRequest("GET", ds_link)["dataStore"]
    # POST a featuretype
    name, title = "timezones", "test feature type 1"
    _, r = APIRequest("POST", ds["href"], {"featureType":{"name":name, "title":title}},
                      get_response=True)
    ft_link = r.getheader("Location").rsplit(".", 1)[0]
    # CoverageStores.
    name, title = "testCS1", "test coverageStore 1"
    _, r = APIRequest("POST", ws["coverageStores"]["href"], {"coverageStore":{"name":name, "title":title}},
                      get_response=True)
    cs_link = r.getheader("Location").rsplit(".", 1)[0]
    # PUT file
    APIRequest("PUT", cs_link + "/file.tif", open("./files/HYP_LR.zip", "rb"),
               encode=None, content_type="application/zip")
    cs = APIRequest("GET", cs_link)["coverageStore"]
    # POST a coverage
    name, title = "HYP_LR", "test coverage 1"
    _, r = APIRequest("POST", cs["href"], {"coverage":{"name":name, "title":title}},
                      get_response=True)
    c_link = r.getheader("Location").rsplit(".", 1)[0]

    #
    # OK, now the actual layer tests.
    #

    layers = APIRequest("GET", target + "/maps/" + map_name + "/layers")["layers"]
    assert len(layers) == 0

    # A first layer for featuretype

    name = "FTlayerTest"
    _, r = APIRequest("POST", target + "/maps/" + map_name + "/layers",
                      {"layer":{"name":name, "resource":{"href":ft_link}}},
                      get_response=True)
    ftl_link = r.getheader("Location").rsplit(".", 1)[0]

    # Check GET.
    ftl = APIRequest("GET", ftl_link)["layer"]
    assert ftl["name"] == name
    assert ftl["type"] == "POLYGON"

    # check GET fields
    fields = APIRequest("GET", ftl_link + "/fields")["fields"]
    assert len(fields) == 15

    # check GET layerstyles
    styles = APIRequest("GET", ftl_link + "/styles")["styles"]
    assert len(styles) == 1

    APIRequest("POST", ftl_link + "/styles", {"style":{"resource":{"href":styles[0]["href"]}}})

    # A second layer for coverage

    name = "ClayerTest"
    _, r = APIRequest("POST", target + "/maps/" + map_name + "/layers",
                      {"layer":{"name":name, "resource":{"href":c_link}}},
                      get_response=True)
    cl_link = r.getheader("Location").rsplit(".", 1)[0]

    # Check GET.
    cl = APIRequest("GET", cl_link)["layer"]
    assert cl["name"] == name
    assert cl["type"] == "RASTER"

    # Check GET.
    layers = APIRequest("GET", target + "/maps/" + map_name + "/layers")["layers"]
    assert len(layers) == 2

    # check GET fields
    fields = APIRequest("GET", cl_link + "/fields")["fields"]
    assert len(fields) == 0

    # check GET layerstyles
    fields = APIRequest("GET", cl_link + "/styles")["styles"]
    assert len(fields) == 0


    # Now lets try layer groups.

    layers = APIRequest("GET", target + "/maps/" + map_name + "/layergroups")["layerGroups"]
    assert len(layers) == 0

    # POST an empty group
    name = "test_group"
    _, r = APIRequest("POST", target + "/maps/" + map_name + "/layergroups", {"layerGroup":{"name":name}}, get_response=True)
    g_link = r.getheader("Location").rsplit(".", 1)[0]

    # GET it.
    group = APIRequest("GET", g_link)["layerGroup"]
    assert group["name"] == name
    assert len(group["layers"]) == 0

    # PUT some new layers in it.
    group["layers"] = [x["name"] for x in group["layers"]] + [ftl["name"]]
    del group["bounds"]
    APIRequest("PUT", g_link, {"layerGroup":group})

    # GET it.
    group = APIRequest("GET", g_link)["layerGroup"]
    assert len(group["layers"]) == 1

    # PUT some new layers in it.
    group["layers"] = [x["name"] for x in group["layers"]] + [cl["name"]]
    del group["bounds"]
    APIRequest("PUT", g_link, {"layerGroup":group})

    # GET it.
    group = APIRequest("GET", g_link)["layerGroup"]
    assert len(group["layers"]) == 2


def test_scenario():

    # utils.default_encoding = "xml"

    target = "http://localhost:8080"
    map_name = "tests"

    # Clean the test file, now we are sure it is empty.
    APIRequest("DELETE", target + "/maps/" + map_name)
    APIRequest("POST", target + "/maps", {"mapfile":{"name":map_name}})

    # _test_workspaces(target, map_name)
    # _test_styles(target, map_name)

    _test_layers(target, map_name)
