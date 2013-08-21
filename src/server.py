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

import os.path

import sys

import web
import json
import urlparse

import mralogs
import logging

import mapfile
from mra import MRA


import webapp
from webapp import HTTPCompatible, urlmap, get_data

import tools
from tools import href, assert_is_empty

from pyxml import Entries


from extensions import plugins


# Some helper functions first.
def get_workspace(ws_name):
    with webapp.mightNotFound():
        return mra.get_workspace(ws_name)

# Now the main classes that handle the REST API.

class index(object):
    @HTTPCompatible()
    def GET(self, format):
        return {
            "workspaces": href("workspaces/"),
            "styles": href("styles/"),
            "layers": href("layers/"),
            "layergroups": href("layergroups/"),
            }


class workspaces(object):
    @HTTPCompatible()
    def GET(self, format, *args, **kwargs):
        return {"workspaces": [{
                    "name": ws_name,
                    "href": "%s/workspaces/%s.%s" % (web.ctx.home, ws_name, format)
                    } for ws_name in mra.list_workspaces()]
                }

    @HTTPCompatible()
    def POST(self, format):
        data = get_data(name="workspace", mandatory=["name"], authorized=["name"])
        ws_name = data.pop("name")

        with webapp.mightConflict():
            mra.create_workspace(ws_name).save()

        webapp.Created("%s/workspaces/%s.%s" % (web.ctx.home, ws_name, format))


class workspace(object):
    @HTTPCompatible()
    def GET(self, ws_name, format):
        ws = get_workspace(ws_name)
        return {"workspace": ({
                    "name": ws.name,
                    "dataStores":
                        href("%s/workspaces/%s/datastores.%s" % (web.ctx.home, ws.name, format)),
                    "coverageStores":
                        href("%s/workspaces/%s/coveragestores.%s" % (web.ctx.home, ws.name, format)),
                    "wmsStores": "", # TODO
                    })
                }


class datastores(object):
    @HTTPCompatible()
    def GET(self, ws_name, format):
        ws = get_workspace(ws_name)
        return {"dataStores": [{
                    "name": ds_name,
                    "href": "%s/workspaces/%s/datastores/%s.%s" % (
                        web.ctx.home, ws.name, ds_name, format)
                    } for ds_name in ws.iter_datastore_names()]
                }

    @HTTPCompatible()
    def POST(self, ws_name, format):
        ws = get_workspace(ws_name)

        data = get_data(name="dataStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        ds_name = data.pop("name")

        with webapp.mightConflict("dataStore", workspace=ws_name):
            ws.create_datastore(ds_name, data)
        ws.save()

        webapp.Created("%s/workspaces/%s/datastores/%s.%s" % (
                web.ctx.home, ws_name, ds_name, format))


class datastore(object):
    @HTTPCompatible()
    def GET(self, ws_name, ds_name, format):
        ws = get_workspace(ws_name)

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            info = ws.get_datastore_info(ds_name)
        connectionParameters = info.get("connectionParameters", {})

        return {"dataStore": {
                    "name": info["name"],
                    "enabled": True, # TODO
                    "__default": False, # TODO
                    "workspace": {
                        "name": ws.name,
                        "href": "%s/workspaces/%s.%s" % (
                            web.ctx.home, ws.name, format),
                        },
                    "featureTypes": href("%s/workspaces/%s/datastores/%s/featuretypes.%s" % (
                                        web.ctx.home, ws.name, ds_name, format)
                        ),
                    "connectionParameters": Entries(connectionParameters, tag_name="entry")
                    }
                }

    @HTTPCompatible()
    def PUT(self, ws_name, ds_name, format):
        ws = get_workspace(ws_name)

        data = get_data(name="dataStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        if ds_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a data store.")

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            ws.update_datastore(ds_name, data)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, ws_name, ds_name, format):
        ws = get_workspace(ws_name)

        # TODO: check, this is not consistent between ds/cs.
        # We need to check if this datastore is empty.
        assert_is_empty(ws.iter_featuretypemodels(ds_name=ds_name), "datastore", ds_name)

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            ws.delete_datastore(ds_name)
        ws.save()


class featuretypes(object):
    @HTTPCompatible()
    def GET(self, ws_name, ds_name, format):
        ws = get_workspace(ws_name)

        return {"featureTypes": [{
                    "name": ft.name,
                    "href": "%s/workspaces/%s/datastores/%s/featuretypes/%s.%s" % (
                        web.ctx.home, ws.name, ds_name, ft.name, format)
                    } for ft in ws.iter_featuretypemodels(ds_name)]
                }

    @HTTPCompatible()
    def POST(self, ws_name, ds_name, format):
        ws = get_workspace(ws_name)

        data = get_data(name="featureType", mandatory=["name"], authorized=["name", "title", "abstract"])
        with webapp.mightConflict("featureType", datastore=ds_name):
            with webapp.mightNotFound("featureType", datastore=ds_name):
                ws.create_featuretypemodel(ds_name, data["name"], data)
        ws.save()

        webapp.Created("%s/workspaces/%s/datastores/%s/featuretypes/%s.%s" % (
                web.ctx.home, ws.name, ds_name, data["name"], format))


class featuretype(object):
    @HTTPCompatible()
    def GET(self, ws_name, ds_name, ft_name, format):
        ws = get_workspace(ws_name)

        ds = ws.get_datastore(ds_name)

        # Checks if postgis table, then adds the schema.
        info = ws.get_datastore_info(ds_name)
        cparam = info["connectionParameters"]
        if cparam.get("dbtype", None) in ["postgis", "postgres", "postgresql"]:
            if cparam.get("schema", ""):
                table = "%s.%s" % (cparam.get("schema", ""), ft_name)
            else:
                table = "public.%s" % ft_name
        else:
            table = ft_name

        with webapp.mightNotFound("dataStore", datastore=ds_name):
            dsft = ds[table]

        with webapp.mightNotFound("featureType", datastore=ds_name):
            ft = ws.get_featuretypemodel(ds_name, ft_name)

        extent = ft.get_extent()
        latlon_extent = ft.get_latlon_extent()

        return {"featureType": ({
                    "name": ft.name,
                    "nativeName": ft.name,
                    "namespace": None, # TODO
                    "title": ft.get_mra_metadata("title", ft.name),
                    "abstract": ft.get_mra_metadata("abstract", None),
                    "keywords": ft.get_mra_metadata("keywords", []),
                    "srs": "%s:%s" % (ft.get_authority()[0], ft.get_authority()[1]),
                    "nativeCRS": ft.get_wkt(),
                    "attributes": [{
                            "name": f.get_name(),
                            "minOccurs": 0 if f.is_nullable() else 1,
                            "maxOccurs": 1,
                            "nillable": f.is_nullable(),
                            "binding": f.get_type_name(),
                            "length": f.get_width(),
                            } for f in dsft.iterfields()],
                    "nativeBoundingBox": {
                        "minx": extent.minX(),
                        "miny": extent.minY(),
                        "maxx": extent.maxX(),
                        "maxy": extent.maxY(),
                        "crs": "%s:%s" % (ft.get_authority_name(), ft.get_authority_code()),
                        },
                    "latLonBoundingBox": {
                        "minx": latlon_extent.minX(),
                        "miny": latlon_extent.minY(),
                        "maxx": latlon_extent.maxX(),
                        "maxy": latlon_extent.maxY(),
                        "crs": "EPSG:4326",
                        },
                    "projectionPolicy": None, # TODO
                    "enabled": True, # TODO
                    "store": { # TODO: add key: class="dataStore"
                        "name": ds_name,
                        "href": "%s/workspaces/%s/datastores/%s.%s" % (
                            web.ctx.home, ws_name, ds_name, format)
                        },
                    "maxFeatures": 0, # TODO
                    "numDecimals": 0, # TODO
                    })
                }

    @HTTPCompatible()
    def PUT(self, ws_name, ds_name, ft_name, format):
        ws = get_workspace(ws_name)

        data = get_data(name="featureType", mandatory=["name"], authorized=["name", "title", "abstract"])
        if ft_name != data["name"]:
            raise webapp.Forbidden("Can't change the name of a feature type.")

        metadata = dict((k, v) for k, v in data.iteritems() if k in ["title", "abstract"])

        with webapp.mightNotFound("featureType", datastore=ds_name):
            ws.update_featuretypemodel(ds_name, ft_name, metadata)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, ws_name, ds_name, ft_name, format):
        ws = get_workspace(ws_name)

        # We need to check if there are any layers using this.
        assert_is_empty(ws.iter_layers(mra={"name":ft_name, "workspace":ws_name, "storage":ds_name,
                                            "type":"featuretype"}),"featuretype", ft_name)

        with webapp.mightNotFound("featureType", datastore=ds_name):
            ws.delete_featuretypemodel(ds_name, ft_name)
        ws.save()


class coveragestores(object):
    @HTTPCompatible()
    def GET(self, ws_name, format):
        ws = get_workspace(ws_name)

        return {"coverageStores": [{
                    "name": cs_name,
                    "href": "%s/workspaces/%s/coveragestores/%s.%s" % (
                        web.ctx.home, ws.name, cs_name, format)
                    } for cs_name in ws.iter_coveragestore_names()]
                }

    @HTTPCompatible()
    def POST(self, ws_name, format):
        ws = get_workspace(ws_name)

        data = get_data(name="coverageStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        cs_name = data.pop("name")

        with webapp.mightConflict("coverageStore", workspace=ws_name):
            ws.create_coveragestore(cs_name, data)
        ws.save()

        webapp.Created("%s/workspaces/%s/coveragestores/%s.%s" % (
                web.ctx.home, ws_name, cs_name, format))


class coveragestore(object):
    @HTTPCompatible()
    def GET(self, ws_name, cs_name, format):
        ws = get_workspace(ws_name)

        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            info = ws.get_coveragestore_info(cs_name)
        connectionParameters = info.get("connectionParameters", {})

        return {"coverageStore": {
                    "name": info["name"],
                    "type": None, # TODO
                    "enabled": True, # TODO
                    "__default": False, # TODO
                    "workspace": {
                        "name": ws.name,
                        "href": "%s/workspaces/%s.%s" % (
                            web.ctx.home, ws.name, format),
                        },
                    "coverages": href("%s/workspaces/%s/coveragestores/%s/coverages.%s" % (
                                    web.ctx.home, ws.name, cs_name, format)
                        ),
                    "connectionParameters": connectionParameters and Entries({
                        "url": info["connectionParameters"]["url"],
                        "namespace": None, # TODO
                        }, tag_name="entry")
                    }
                }


    @HTTPCompatible()
    def PUT(self, ws_name, cs_name, format):
        ws = get_workspace(ws_name)

        data = get_data(name="coverageStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        if cs_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a coverage store.")

        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            ws.update_coveragestore(cs_name, data)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, ws_name, cs_name, format):
        ws = get_workspace(ws_name)

        # TODO: check, this is not consistent between ds/cs.
        # We need to check if this datastore is empty.
        assert_is_empty(ws.iter_coverages(cs_name=cs_name), "coveragestore", ds_name)

        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            ws.delete_coveragestore(cs_name)
        ws.save()


class coverages(object):
    @HTTPCompatible()
    def GET(self, ws_name, cs_name, format):
        ws = get_workspace(ws_name)

        return {"coverages": [{
                    "name": c.name,
                    "href": "%s/workspaces/%s/coveragestores/%s/coverages/%s.%s" % (
                        web.ctx.home, ws.name, cs_name, c.name, format)
                    } for c in ws.iter_coveragemodels(cs_name)]
                }

    @HTTPCompatible()
    def POST(self, ws_name, cs_name, format):
        ws = get_workspace(ws_name)

        data = get_data(name="coverage", mandatory=["name"], authorized=["name", "title", "abstract"])

        with webapp.mightConflict("coverage", coveragestore=cs_name):
            with webapp.mightNotFound("coverage", coveragestore=cs_name):
                ws.create_coveragemodel(data["name"], cs_name, data)
        ws.save()

        webapp.Created("%s/workspaces/%s/coveragestores/%s/coverages/%s.%s" % (
                web.ctx.home, ws.name, cs_name, data["name"], format))


class coverage(object):
    @HTTPCompatible()
    def GET(self, ws_name, cs_name, c_name, format):
        ws = get_workspace(ws_name)

        # with webapp.mightNotFound("coveragestore", workspace=ws_name):
        #     cs = ws.get_coveragestore(cs_name)

        with webapp.mightNotFound("coverage", coveragestore=cs_name):
            c = ws.get_coveragemodel(c_name, cs_name)

        extent = c.get_extent()
        latlon_extent = c.get_latlon_extent()

        return {"coverage": ({
                    "name": c.name,
                    "nativeName": c.name,
                    "namespace": None, # TODO
                    "title": c.get_mra_metadata("title", c.name),
                    "abstract": c.get_mra_metadata("abstract", None),
                    "keywords": c.get_mra_metadata("keywords", []),
                    "nativeCRS": c.get_wkt(), # TODO: Add key class="projected" if projected...
                    "srs": "%s:%s" % (c.get_authority_name(), c.get_authority_code()),
                    "nativeBoundingBox": {
                        "minx": extent.minX(),
                        "miny": extent.minY(),
                        "maxx": extent.maxX(),
                        "maxy": extent.maxY(),
                        "crs": "%s:%s" % (c.get_authority_name(), c.get_authority_code()), # TODO: Add key class="projected" if projected...
                        },
                    "latLonBoundingBox":{
                        "minx": latlon_extent.minX(),
                        "miny": latlon_extent.minY(),
                        "maxx": latlon_extent.maxX(),
                        "maxy": latlon_extent.maxY(),
                        "crs": "EPSG:4326"
                        },
                    "enabled": True, # TODO
                    "metadata": None, # TODO
                    "store": { # TODO: Add attr class="coverageStore"
                        "name": cs_name,
                        "href": "%s/workspaces/%s/coveragestores/%s.%s" % (
                            web.ctx.home, ws_name, cs_name, format)
                        },
                    "nativeFormat": None, # TODO
                    "grid": { # TODO: Add attr dimension
                        "range": {
                            "low": None, # TODO
                            "high": None, # TODO
                            },
                        "transform": {
                            "scaleX": None, # TODO
                            "scaleY": None, # TODO
                            "shearX": None, # TODO
                            "shearY": None, # TODO
                            "translateX": None, # TODO
                            "translateY": None, # TODO
                            },
                        "crs": None,
                        },
                    "supportedFormats": [], # TODO
                    "interpolationMethods": [], # TODO
                    "defaultInterpolationMethod": None,
                    "dimensions": [], # TODO
                    "projectionPolicy": None, # TODO
                    "requestSRS": None, # TODO
                    "responseSRS": None, # TODO
                    })
                }

    @HTTPCompatible()
    def PUT(self, ws_name, cs_name, c_name, format):
        ws = get_workspace(ws_name)

        data = get_data(name="coverage", mandatory=["name"], authorized=["name", "title", "abstract"])
        if c_name != data["name"]:
            raise webapp.Forbidden("Can't change the name of a coverage.")


        metadata = dict((k, v) for k, v in data.iteritems() if k in ["title", "abstract"])

        with webapp.mightNotFound("coverage", coveragestore=cs_name):
            ws.update_coveragemodel(c_name, cs_name, metadata)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, ws_name, cs_name, c_name, format):
        ws = get_workspace(ws_name)

        # We need to check if there are any layers using this.
        assert_is_empty(ws.iter_layers(mra={"name":c_name, "workspace":ws_name, "storage":cs_name,
                                            "type":"coverage"}), "coverage", ft_name)

        with webapp.mightNotFound("coverage", coveragestore=cs_name):
            ws.delete_coveragemodel(c_name, cs_name)
        ws.save()


class files(object):

    @HTTPCompatible(allow_all=True)
    def PUT(self, ws_name, st_type, st_name, f_type, format):
        import zipfile

        # TODO: According to geoserv's examples we might have to handle
        # directories as well as files, in that case we want to upload
        # all the files from the directory.

        # Lets first try to get the file.
        if f_type == "file":
            # Check if zip or not...
            data = web.data()
        elif f_type == "url":
            raise webapp.NotImplemented()
        elif f_type == "external":
            raise webapp.NotImplemented()

        ws = get_workspace(ws_name)

        # Now we make sure the store exists.
        try:
            ws.get_store_info(st_type, st_name)
        except KeyError:
            # Create the store if it seems legit and it does not exist.
            if st_type == "datastores" or st_type == "coveragestores":
                st_type = st_type[:-1] # Remove trailing 's'
                with webapp.mightConflict("dataStore", workspace=ws_name):
                    ws.create_store(st_type, st_name, {})
            # Finaly check if its OK now.
            with webapp.mightNotFound(message="Store {exception} does not exist "
                                      "and it could not be created."):
                ws.get_store_info(st_type, st_name)

        # Then we store the file.
        ext = web.ctx.env.get('CONTENT_TYPE', '').split("/")[-1]
        path = mra.create_file(st_name + (".%s" % ext) if ext else "", data=data)
        dest = os.path.join(os.path.split(path)[0], st_name)

        # We also unzip it if its ziped.
        ctype = web.ctx.env.get('CONTENT_TYPE', None)
        if ctype == "application/zip":
            z = zipfile.ZipFile(path)
            for f in z.namelist():
                fp = mra.mk_path(mra.get_file_path(st_name, f))

                # If the file has the correct target we might want it.
                if format and fp.endswith(format) and not tools.is_hidden(fp):
                    path = fp

                z.extract(f, path=dest)

        # Set new connection parameters:
        ws.update_store(st_type, st_name, {"connectionParameters":{"url":"file:"+mra.pub_file_path(path)}})
        ws.save()

        # Finally we might have to configure it.
        params = web.input(configure="none")
        if params.configure == "first":
            raise webapp.NotImplemented()
        elif params.configure == "none":
            pass
        elif params.configure == "all":
            raise webapp.NotImplemented()
        else:
            raise webapp.BadRequest(message="configure must be one of 'first', 'none' or 'all'.")


class styles(object):
    @HTTPCompatible()
    def GET(self, format):
        return {"styles": [{
                    "name": s_name,
                    "href": "%s/styles/%s.%s" % (web.ctx.home, s_name, format)
                    } for s_name in mra.list_styles()]
                }

    @HTTPCompatible()
    def POST(self, format):
        params = web.input(name=None)
        name = params.name
        if name == None:
            raise webapp.BadRequest(message="no parameter 'name' given.")

        data = web.data()
        mra.create_style(name, data)


class style(object):
    @HTTPCompatible(authorize=["sld"])
    def GET(self, s_name, format):
        with webapp.mightNotFound():
            style = mra.get_style(s_name)

        if format == "sld":
            return style

        return {"style": {
                    "name": s_name,
                    "sldVersion": Entries(["1.0.0"], tag_name="version"),
                    "filename": s_name + ".sld",
                    }
                }

    @HTTPCompatible()
    def PUT(self, s_name, format):
        #TODO: Also update layers using this style.
        with webapp.mightNotFound():
            mra.delete_style(s_name)
        data = web.data()
        mra.create_style(s_name, data)

    @HTTPCompatible()
    def DELETE(self, s_name, format):
        #TODO: Maybe check for layers using this style?
        with webapp.mightNotFound():
            mra.delete_style(s_name)


class layers(object):
    @HTTPCompatible()
    def GET(self, format):
        mf = mra.get_available()
        return {"layers": [{
                    "name": layer.ms.name,
                    "href": "%s/layers/%s.%s" % (web.ctx.home, layer.ms.name, format),
                    } for layer in mf.iter_layers()]
                }

    @HTTPCompatible()
    def POST(self, format):
        data = get_data(name="layer",
                        mandatory=["name", "resource"],
                        authorized=["name", "title", "abstract", "resource", "enabled"])

        l_name = data.pop("name")
        l_enabled = data.pop("enabled", True)

        href = data["resource"]["href"]
        try:
            ws_name, st_type, st_name, r_type, r_name = mra.href_parse(href, 5)
        except ValueError:
            raise webapp.NotFound(message="ressource '%s' was not found." % href)

        st_type, r_type = st_type[:-1], r_type[:-1] # Remove trailing s.

        ws = get_workspace(ws_name)
        with webapp.mightNotFound(r_type, workspace=ws_name):
            try:
                model = ws.get_layermodel(r_type, st_name, r_name)
            except ValueError:
                raise KeyError(r_type)

        mf = mra.get_available()
        with webapp.mightConflict():
            mf.create_layer(model, l_name, l_enabled)
        mf.save()

        webapp.Created("%s/layers/%s.%s" % (web.ctx.home, l_name, format))


class layer(object):
    @HTTPCompatible()
    def GET(self, l_name, format):
        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)

        data_type, store_type = {
            "featuretype": ("featuretype", "datastore"),
            "coverage": ("coverage", "coveragestore")
            }[layer.get_mra_metadata("type")]

        return {"layer" : {
                    "name": l_name,
                    "path": "/", # TODO
                    "type": layer.get_type_name(),
                    "defaultStyle": {
                        "name": layer.ms.classgroup,
                        "href": "%s/styles/%s.%s" % (web.ctx.home, layer.ms.classgroup, format),
                        },
                    "styles": [{ # TODO: Add attr class="linked-hash-set"
                            "name": s_name,
                            "href": "%s/styles/%s.%s" % (web.ctx.home, s_name, format),
                            } for s_name in layer.iter_styles()],
                    "resource": { # TODO: Add attr class="featureType|coverage"
                        "name": layer.get_mra_metadata("name"),
                        "href": "%s/workspaces/%s/%ss/%s/%ss/%s.%s" % (
                            web.ctx.home, layer.get_mra_metadata("workspace"),
                            store_type, layer.get_mra_metadata("storage"), data_type, layer.get_mra_metadata("name"), format),
                        },
                    "enabled": bool(layer.ms.status),
                    "attribution": { # TODO
                        "logoWidth": 0,
                        "logoHeight": 0,
                        },
                    }
                }

    @HTTPCompatible()
    def PUT(self, l_name, format):
        mf = mra.get_available()

        data = get_data(name="layer", mandatory=["name", "resource"],
                        authorized=["name", "title", "abstract", "resource", "enabled"])
        if l_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a layer.")

        l_enabled = data.pop("enabled", True)


        href = data["resource"]["href"]
        try:
            ws_name, st_type, st_name, r_type, r_name = mra.href_parse(href, 5)
        except ValueError:
            raise webapp.NotFound(message="ressource '%s' was not found." % href)

        st_type, r_type = st_type[:-1], r_type[:-1] # Remove trailing s.

        ws = get_workspace(ws_name)
        with webapp.mightNotFound(r_type, workspace=ws_name):
            try:
                model = ws.get_layermodel(r_type, st_name, r_name)
            except ValueError:
                raise KeyError(r_type)

        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)
            if layer.get_mra_metadata("type") != r_type:
                raise webapp.BadRequest("Can't change a '%s' layer into a '%s'."
                                        % (layer.get_mra_metadata("type"), r_type))
            model.configure_layer(layer, l_enabled)
        mf.save()

    @HTTPCompatible()
    def DELETE(self, l_name, format):
        mf = mra.get_available()
        with webapp.mightNotFound():
            mf.delete_layer(l_name)
        mf.save()


class layerstyles(object):
    @HTTPCompatible()
    def GET(self, l_name, format):
        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)

        if format == "sld":
            return layer.getSLD()

        return {"styles": [{
                    "name": s_name,
                    "href": "%s/styles/%s.%s" % (web.ctx.home, s_name, format),
                    } for s_name in layer.iter_styles()],
                }

    @HTTPCompatible()
    def POST(self, l_name, format):
        data = get_data(name="style", mandatory=["resource"],
                        authorized=["name", "title", "abstract", "resource"])

        href = data["resource"]["href"]
        try:
            _, s_name = mra.href_parse(href, 2)
        except ValueError:
            raise webapp.NotFound(message="style '%s' was not found." % href)

        with webapp.mightNotFound():
            style = mra.get_style(s_name)

        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)

        layer.add_style_sld(mf, s_name, style)
        mf.save()

        webapp.Created("%s/layers/%s/layerstyles/%s.%s" % (web.ctx.home, l_name, s_name, format))


class layerstyle(object):
    @HTTPCompatible()
    def DELETE(self, l_name, s_name, format):
        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)
        with webapp.mightNotFound("style", layer=l_name):
            layer.remove_style(s_name)
        mf.save()


class layerfields(object):
    @HTTPCompatible()
    def GET(self, l_name, format):
        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)

        return {"fields": [{
                    "name": layer.get_metadata("gml_%s_alias" % field, None),
                    "fieldType": layer.get_metadata("gml_%s_type" % field, None),
                    } for field in layer.iter_fields()]
                }


class layergroups(object):
    @HTTPCompatible()
    def GET(self, format):
        mf = mra.get_available()

        return {"layerGroups" : [{
                    "name": lg.name,
                    "href": "%s/layergroups/%s.%s" % (web.ctx.home, lg.name, format)
                    } for lg in mf.iter_layergroups()]
                }

    @HTTPCompatible()
    def POST(self, format):
        mf = mra.get_available()

        data = get_data(name="layerGroup", mandatory=["name"], authorized=["name", "title", "abstract", "layers"])
        lg_name = data.pop("name")
        layers = [mf.get_layer(l_name) for l_name in data.pop("layers", [])]

        with webapp.mightConflict():
            lg = mf.create_layergroup(lg_name, data)
        lg.add(*layers)

        mf.save()

        webapp.Created("%s/layergroups/%s.%s" % (web.ctx.home, lg.name, format))


class layergroup(object):

    @HTTPCompatible()
    def GET(self, lg_name, format):
        mf = mra.get_available()
        with webapp.mightNotFound():
            lg = mf.get_layergroup(lg_name)

        latlon_extent = lg.get_latlon_extent()

        return {"layerGroup": ({
                    "name": lg.name,
                    "mode": None, # TODO
                    "publishables": [{
                            "name": layer.ms.name,
                            "href": "%s/layers/%s.%s" % (web.ctx.home, layer.ms.name, format),
                            } for layer in lg.iter_layers()],
                    "bounds": {
                        "minx": latlon_extent.minX(),
                        "miny": latlon_extent.minY(),
                        "maxx": latlon_extent.maxX(),
                        "maxy": latlon_extent.maxY(),
                        "crs": "EPSG:4326",
                        },
                    "styles": [],
                    })
                }

    @HTTPCompatible()
    def PUT(self, lg_name, format):
        mf = mra.get_available()

        with webapp.mightNotFound():
            lg = mf.get_layergroup(lg_name)

        data = get_data(name="layerGroup", mandatory=["name"], authorized=["name", "title", "abstract", "layers"])
        if lg_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a layergroup.")

        layers = data.pop("layers", [])
        if not isinstance(layers, list) or any(not isinstance(x, basestring) for x in layers):
            raise webapp.BadRequest("layers must be a list of layer names.")

        lg.clear()
        lg.add(*layers)

        mf.save()

    @HTTPCompatible()
    def DELETE(self, lg_name, format):

        mf = mra.get_available()
        with webapp.mightNotFound():
            mf.delete_layergroup(lg_name)
        mf.save()


class OWSGlobalSettings(object):

    @HTTPCompatible()
    def GET(self, ows, format):
        mf = mra.get_available()
        try:
            if mf.get_metadata("%s_enable_request" % ows) == "*":
                is_enabled = True
        except:
            is_enabled = False

        return { 
            ows: {
                "enabled": is_enabled,
                "name": ows,
                "schemaBaseURL": mf.get_metadata("ows_schemas_location", "http://schemas.opengis.net"),
                }
            }
    
    @HTTPCompatible()
    def PUT(self, ows, format):
        mf = mra.get_available()
        data = get_data(name=ows, mandatory=["enabled"], authorized=["enabled"])
        is_enabled = data.pop("enabled")
        values = {True: "*", "true": "*", False: "", "false": ""}
        if is_enabled not in values:
            raise KeyError("'%s' is not valid" % is_enabled)
        mf.set_metadata("%s_enable_request" % ows, values[is_enabled])
        mf.save()


class OWSSettings(object):

    @HTTPCompatible()
    def GET(self, ows, ws_name, format):
        ws = get_workspace(ws_name)
        try:
            if ws.get_metadata("%s_enable_request" % ows) == "*":
                is_enabled = True
        except:
            is_enabled = False

        return {
            ows: {
                "enabled": is_enabled,
                "name": ows,
                "schemaBaseURL": ws.get_metadata("ows_schemas_location", "http://schemas.opengis.net"),
                }
            }

    @HTTPCompatible()
    def PUT(self, ows, ws_name, format):
        ws = get_workspace(ws_name)
        data = get_data(name=ows, mandatory=["enabled"], authorized=["enabled"])
        is_enabled = data.pop("enabled")
        values = {True: "*", "true": "*", False: "", "false": ""}
        if is_enabled not in values:
            raise KeyError("'%s' is not valid" % is_enabled)
        ws.set_metadata("%s_enable_request" % ows, values[is_enabled])
        ws.save()

    @HTTPCompatible()
    def DELETE(self, ows, ws_name, format):
        ws = get_workspace(ws_name)
        ws.set_metadata("%s_enable_request" % ows, "")
        ws.save()

# Index:
urlmap(index, "")

# Workspaces:
urlmap(workspaces, "workspaces")
urlmap(workspace, "workspaces", ())

# Datastores:
urlmap(datastores, "workspaces", (), "datastores")
urlmap(datastore, "workspaces", (), "datastores", ())
# Featuretypes:
urlmap(featuretypes, "workspaces", (), "datastores", (), "featuretypes")
urlmap(featuretype, "workspaces", (), "datastores", (), "featuretypes", ())

# Coveragestores:
urlmap(coveragestores, "workspaces", (), "coveragestores")
urlmap(coveragestore, "workspaces", (), "coveragestores", ())
# Coverages:
urlmap(coverages, "workspaces", (), "coveragestores", (), "coverages")
urlmap(coverage, "workspaces", (), "coveragestores", (), "coverages", ())

# Files:
urlmap(files, "workspaces", (), "(datastores|coveragestores)", (), "(file|url|external)")

# Styles:
urlmap(styles, "styles")
urlmap(style, "styles", ())

# Layers, layer styles and data fields:
urlmap(layers, "layers")
urlmap(layer, "layers", ())
urlmap(layerstyles, "layers", (), "styles")
urlmap(layerstyle, "layers", (), "styles", ())
urlmap(layerfields, "layers", (), "fields")

# Layergroups:
urlmap(layergroups, "layergroups")
urlmap(layergroup, "layergroups", ())

# OGC Web Services:
urlmap(OWSGlobalSettings, "services", "(wms|wfs|wcs)", "settings")
urlmap(OWSSettings, "services", "(wms|wfs|wcs)", (), "settings")

urls = tuple(urlmap)


mra = MRA(os.path.join(sys.path[0], "mra.yaml"))

mralogs.setup(mra.config["logging"]["level"], mra.config["logging"]["file"],
              mra.config["logging"]["format"])

web.config.debug = mra.config["debug"].get("web_debug", False)
webapp.exceptionManager.raise_all = mra.config["debug"].get("raise_all", False)
HTTPCompatible.return_logs = mra.config["logging"].get("web_logs", False)

for pdir in mra.config["plugins"].get("loadpaths", []):
    plugins.load_plugins_dir(pdir)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()

application = app.wsgifunc()
