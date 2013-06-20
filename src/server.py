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

import web
import json
import urlparse

import mralogs
import logging

import mapfile

import webapp
from webapp import HTTPCompatible, urlmap, get_data

import tools
from tools import get_mapfile, get_mapfile_workspace, get_config, href, assert_is_empty

from pyxml import Entries


from extensions import plugins

mralogs.setup(get_config("logging")["level"], get_config("logging")["file"],
              get_config("logging")["format"])

class index(object):
    def GET(self, format):
        return "This is MRA."

class mapfiles(object):
    @HTTPCompatible()
    def GET(self, format):
        mapfiles = []
        for path in tools.get_mapfile_paths():
            try:
                mf = mapfile.Mapfile(path)
            except IOError, OSError:
                continue
            filename = mf.filename.replace(".map", "")
            mapfiles.append({
                "name": filename,
                "href": "%s/maps/%s.%s" % (web.ctx.home, filename, format)
              })

        return {"mapfiles": mapfiles}

    @HTTPCompatible()
    def POST(self, format):
        data = get_data(name="mapfile", mandatory=["name"], authorized=["name", "title", "abstract"])

        map_name = data.pop("name")
        path = tools.mk_mapfile_path(map_name)

        with webapp.mightConflict(message="Mapfile '{exception}' already exists."):
            mapfile.create_mapfile(path, map_name, data)

        webapp.Created("%s/maps/%s%s" % (web.ctx.home, map_name, (".%s" % format) if format else ""))


class named_mapfile(object):
    @HTTPCompatible(authorize=["map"], default="html")
    def GET(self, map_name, format, *args, **kwargs):

        mf = get_mapfile(map_name)
        with open(mf.path, "r") as f:
            data = f.read()
        return {"mapfile": ({
                "name": map_name,
                "href": "%s/maps/%s.map" % (web.ctx.home, map_name),
                "workspaces": href("%s/maps/%s/workspaces.%s" % (web.ctx.home, map_name, format)),
                "layers": href("%s/maps/%s/layers.%s" % (web.ctx.home, map_name, format)),
                "layergroups": href("%s/maps/%s/layergroups.%s" % (web.ctx.home, map_name, format)),
                "styles": href("%s/maps/%s/styles.%s" % (web.ctx.home, map_name, format)),
                "wms_capabilities": href("%smap=%s&REQUEST=GetCapabilities&VERSION=%s&SERVICE=WMS" % (
                            get_config("mapserver")["url"], mf.path, get_config("mapserver")["wms_version"])),
                "wfs_capabilities": href("%smap=%s&REQUEST=GetCapabilities&VERSION=%s&SERVICE=WFS" % (
                            get_config("mapserver")["url"], mf.path, get_config("mapserver")["wfs_version"])),
                "wcs_capabilities": href("%smap=%s&REQUEST=GetCapabilities&VERSION=%s&SERVICE=WCS" % (
                            get_config("mapserver")["url"], mf.path, get_config("mapserver")["wcs_version"])),
                    })
            } if format != "map" else data

    @HTTPCompatible()
    def PUT(self, map_name, format):
        mf = get_mapfile(map_name)
        path = tools.mk_mapfile_path(map_name)

        data = get_data(name="mapfile", mandatory=["name"], authorized=["name", "title", "abstract"])
        if map_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a mapfile.")

        mf.update(data)
        mf.save()

    @HTTPCompatible()
    def DELETE(self, map_name, format):
        mf = get_mapfile(map_name)

        # TODO: We need to check if this mapfile is empty.
        with webapp.mightNotFound("Mapfile", mapfile=map_name):
            os.remove(mf.path)


class workspaces(object):
    @HTTPCompatible()
    def GET(self, map_name, format, *args, **kwargs):
        mf = get_mapfile(map_name)
        return {"workspaces": [{
                    "name": ws.name,
                    "href": "%s/maps/%s/workspaces/%s.%s" % (web.ctx.home, map_name, ws.name, format)
                    } for ws in mf.iter_workspaces()]
                }


class workspace(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)
        return {"workspace": ({
                    "name": ws.name,
                    "dataStores":
                        href("%s/maps/%s/workspaces/%s/datastores.%s" % (web.ctx.home, map_name, ws.name, format)),
                    "coverageStores":
                        href("%s/maps/%s/workspaces/%s/coveragestores.%s" % (web.ctx.home, map_name, ws.name, format)),
                    "wmsStores": "", # TODO
                    })
                }


class datastores(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, format, *args, **kwargs):
        mf, ws = get_mapfile_workspace(map_name, ws_name)
        return {"dataStores": [{
                    "name": ds_name,
                    "href": "%s/maps/%s/workspaces/%s/datastores/%s.%s" % (
                        web.ctx.home, map_name, ws.name, ds_name, format)
                    } for ds_name in ws.iter_datastore_names()]
                }

    @HTTPCompatible()
    def POST(self, map_name, ws_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        data = get_data(name="dataStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        ds_name = data.pop("name")

        with webapp.mightConflict("dataStore", workspace=ws_name):
            ws.create_datastore(ds_name, data)
        ws.save()

        webapp.Created("%s/maps/%s/workspaces/%s/datastores/%s%s" % (
                web.ctx.home, map_name, ws_name, ds_name, (".%s" % format) if format else ""))


class datastore(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, ds_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            info = ws.get_datastore_info(ds_name)

        return {"dataStore": {
                    "name": info["name"],
                    "enabled": True, # TODO
                    "__default": False, # TODO
                    "workspace": {
                        "name": ws.name,
                        "href": "%s/maps/%s/workspaces/%s.%s" % (
                            web.ctx.home, map_name, ws.name, format),
                        },
                    "featureTypes": href("%s/maps/%s/workspaces/%s/datastores/%s/featuretypes.%s" % (
                                        web.ctx.home, map_name, ws.name, ds_name, format)
                        ),
                    "connectionParameters": Entries({
                        "url": info["connectionParameters"]["url"],
                        "namespace": None, # TODO
                        }, tag_name="entry")
                    }
                }

    @HTTPCompatible()
    def PUT(self, map_name, ws_name, ds_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        data = get_data(name="dataStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        if ds_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a data store.")

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            ws.update_datastore(ds_name, data)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, map_name, ws_name, ds_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        # We need to check if this datatore is empty.
        assert_is_empty(ws.iter_featuretypemodels(ds_name=ds_name), "datastore", ds_name)

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            ws.delete_datastore(ds_name)
        ws.save()


class featuretypes(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, ds_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)
        return {"featureTypes": [{
                    "name": ft.name,
                    "href": "%s/maps/%s/workspaces/%s/datastores/%s/featuretypes/%s.%s" % (
                        web.ctx.home, map_name, ws.name, ds_name, ft.name, format)
                    } for ft in ws.iter_featuretypemodels(ds_name)]
                }

    @HTTPCompatible()
    def POST(self, map_name, ws_name, ds_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        data = get_data(name="featureType", mandatory=["name"], authorized=["name", "title", "abstract"])
        with webapp.mightConflict("featureType", datastore=ds_name):
            with webapp.mightNotFound("featureType", datastore=ds_name):
                ws.create_featuretypemodel(data["name"], ds_name, data)
        ws.save()

        webapp.Created("%s/maps/%s/workspaces/%s/datastores/%s/featuretypes/%s%s" % (
                web.ctx.home, map_name, ws.name, ds_name, data["name"], (".%s" % format) if format else ""))


class featuretype(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, ds_name, ft_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        ds = ws.get_datastore(ds_name)
        with webapp.mightNotFound("dataStore", datastore=ds_name):
            dsft = ds[ft_name]

        with webapp.mightNotFound("featureType", datastore=ds_name):
            ft = ws.get_featuretypemodel(ft_name, ds_name)

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
                        "href": "%s/maps/%s/workspaces/%s/datastores/%s.%s" % (
                            web.ctx.home, map_name, ws_name, ds_name, format)
                        },
                    "maxFeatures": 0, # TODO
                    "numDecimals": 0, # TODO
                    })
                }

    @HTTPCompatible()
    def PUT(self, map_name, ws_name, ds_name, ft_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        data = get_data(name="featureType", mandatory=["name"], authorized=["name", "title", "abstract"])
        if ft_name != data["name"]:
            raise webapp.Forbidden("Can't change the name of a feature type.")

        metadata = dict((k, v) for k, v in data.iteritems() if k in ["title", "abstract"])

        with webapp.mightNotFound("featureType", datastore=ds_name):
            ws.update_featuretypemodel(ft_name, ds_name, metadata)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, map_name, ws_name, ds_name, ft_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        # We need to check if there are any layers using this.
        assert_is_empty(mf.iter_layers(mra={"name":ft_name, "workspace":ws_name, "storage":ds_name, "type":"featuretype"}),"featuretype", ft_name)

        with webapp.mightNotFound("featureType", datastore=ds_name):
            ws.delete_featuretypemodel(ft_name, ds_name)
        ws.save()


class coveragestores(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        return {"coverageStores": [{
                    "name": cs_name,
                    "href": "%s/maps/%s/workspaces/%s/coveragestores/%s.%s" % (
                        web.ctx.home, map_name, ws.name, cs_name, format)
                    } for cs_name in ws.iter_coveragestore_names()]
                }

    @HTTPCompatible()
    def POST(self, map_name, ws_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        data = get_data(name="coverageStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        cs_name = data.pop("name")

        with webapp.mightConflict("coverageStore", workspace=ws_name):
            ws.create_coveragestore(cs_name, data)
        ws.save()

        webapp.Created("%s/maps/%s/workspaces/%s/coveragestores/%s%s" % (
                web.ctx.home, map_name, ws_name, cs_name, (".%s" % format) if format else ""))


class coveragestore(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, cs_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            info = ws.get_coveragestore_info(cs_name)

        return {"coverageStore": {
                    "name": info["name"],
                    "type": None, # TODO
                    "enabled": True, # TODO
                    "__default": False, # TODO
                    "workspace": {
                        "name": ws.name,
                        "href": "%s/maps/%s/workspaces/%s.%s" % (
                            web.ctx.home, map_name, ws.name, format),
                        },
                    "coverages": href("%s/maps/%s/workspaces/%s/coveragestores/%s/coverages.%s" % (
                                    web.ctx.home, map_name, ws.name, cs_name, format)
                        ),
                    "connectionParameters": Entries({
                        "url": info["connectionParameters"]["url"],
                        "namespace": None, # TODO
                        }, tag_name="entry")
                    }
                }



    @HTTPCompatible()
    def PUT(self, map_name, ws_name, cs_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        data = get_data(name="coverageStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        if cs_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a coverage store.")

        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            ws.update_coveragestore(cs_name, data)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, map_name, ws_name, cs_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        # We need to check if this datatore is empty.
        assert_is_empty(ws.iter_coverages(cs_name=cs_name), "coveragestore", ds_name)

        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            ws.delete_coveragestore(cs_name)
        ws.save()


class coverages(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, cs_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)
        return {"coverages": [{
                    "name": c.name,
                    "href": "%s/maps/%s/workspaces/%s/coveragestores/%s/coverages/%s.%s" % (
                        web.ctx.home, map_name, ws.name, cs_name, c.name, format)
                    } for c in ws.iter_coveragemodels(cs_name)]
                }

    @HTTPCompatible()
    def POST(self, map_name, ws_name, cs_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        data = get_data(name="coverage", mandatory=["name"], authorized=["name", "title", "abstract"])

        with webapp.mightConflict("coverage", coveragestore=cs_name):
            ws.create_coveragemodel(data["name"], cs_name, data)
        ws.save()

        webapp.Created("%s/maps/%s/workspaces/%s/coveragestores/%s/coverages/%s%s" % (
                web.ctx.home, map_name, ws.name, cs_name, data["name"], (".%s" % format) if format else ""))


class coverage(object):
    @HTTPCompatible()
    def GET(self, map_name, ws_name, cs_name, c_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

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
                        "href": "%s/maps/%s/workspaces/%s/coveragestores/%s.%s" % (
                            web.ctx.home, map_name, ws_name, cs_name, format)
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
    def PUT(self, map_name, ws_name, cs_name, c_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        data = get_data(name="coverage", mandatory=["name"], authorized=["name", "title", "abstract"])
        if c_name != data["name"]:
            raise webapp.Forbidden("Can't change the name of a coverage.")


        metadata = dict((k, v) for k, v in data.iteritems() if k in ["title", "abstract"])

        with webapp.mightNotFound("coverage", coveragestore=cs_name):
            ws.update_coveragemodel(c_name, cs_name, metadata)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, map_name, ws_name, cs_name, c_name, format):
        mf, ws = get_mapfile_workspace(map_name, ws_name)

        # We need to check if there are any layers using this.
        assert_is_empty(mf.iter_layers(mra={"name":c_name, "workspace":ws_name, "storage":cs_name, "type":"coverage"}),
                        "coverage", ft_name)

        with webapp.mightNotFound("coverage", coveragestore=cs_name):
            ws.delete_coveragemodel(c_name, cs_name)
        ws.save()


class files(object):

    @HTTPCompatible(allow_all=True)
    def PUT(self, map_name, ws_name, st_type, st_name, f_type, format):
        import zipfile

        mf, ws = get_mapfile_workspace(map_name, ws_name)

        # TODO: According to geoserv's examples we might have to handle
        # directories as well as files, in that case we want to upload
        # all the files from the directory.

        # Lets first try to get the file.
        if f_type == "file":
            # Check if zip or not...
            data = web.data()
        elif f_type == "url":
            raise NotImplemented()
        elif f_type == "external":
            raise NotImplemented()

        # Now we make sure the store exists.
        with webapp.mightNotFound(message="Store {exception} does not exist "
                                  "and automatic creation is not yet suported."):
            ws.get_store_info(st_type, st_name)
            # TODO: Create the store if it does not exist.

        # Then we store the file.
        ext = web.ctx.env.get('CONTENT_TYPE', '').split("/")[-1]
        path = tools.mk_st_data_path(ws_name, st_type, st_name, st_name + (".%s" % ext) if ext else "")
        with open(path, "w") as f:
            f.write(data)

        # We also unzip it if its ziped.
        ctype = web.ctx.env.get('CONTENT_TYPE', None)
        if ctype == "application/zip":
            z = zipfile.ZipFile(path)
            for f in z.namelist():
                fp = tools.mk_st_data_path(ws_name, st_type, st_name, f)

                # If the file has the correct target we might want it.
                if format and fp.endswith(format) and not tools.is_hidden(fp):
                    path = fp

                z.extract(f, path=tools.get_st_data_path(ws_name, st_type, st_name))

        # Set new connection parameters:
        ws.update_store(st_type, st_name, {"connectionParameters":{"url":"file:"+tools.no_res_root(path)}})
        ws.save()

        # Finally we might have to configure it.
        params = web.input(configure="none")
        if params.configure == "first":
            raise NotImplemented()
        elif params.configure == "none":
            pass
        elif params.configure == "all":
            raise NotImplemented()
        else:
            raise webapp.BadRequest(message="configure must be one of first, none or all.")


class styles(object):
    @HTTPCompatible()
    def GET(self, map_name, format):
        mf = get_mapfile(map_name)

        return {"styles": [{
                    "name": os.path.basename(os.path.basename(s_name)),
                    "href": "%s/maps/%s/styles/%s.%s" % (web.ctx.home, map_name, os.path.basename(s_name), format)
                    } for s_name in tools.iter_styles(mf)]
                }

    @HTTPCompatible()
    def POST(self, map_name, format):
        mf = get_mapfile(map_name)

        params = web.input(name=None)
        name = params.name
        if name == None:
            raise webapp.BadRequest(message="no parameter 'name' given.")
        with webapp.mightConflict(message="style {exception} already exists."):
            if name in tools.iter_styles(mf):
                raise webapp.KeyExists(name)

        data = web.data()
        path = tools.mk_style_path(name)

        with open(path, "w") as f:
            f.write(data)


class style(object):
    @HTTPCompatible(authorize=["sld"])
    def GET(self, map_name, s_name, format):
        mf = get_mapfile(map_name)

        if format == "sld":
            # We look for styles on disk and in the mapfiles.
            try:
                return open(tools.get_style_path(s_name)).read()
            except IOError, OSError:
                with webapp.mightNotFound("style", mapfile=map_name):
                    return mf.get_style_sld(s_name)

        # We still need to check if this actually exists...
        with webapp.mightNotFound("style", mapfile=map_name):
            if not os.path.exists(tools.get_style_path(s_name)) and not s_name in mf.iter_styles():
                raise KeyError(s_name)

        return {"style": {
                    "name": s_name,
                    "sldVersion": Entries(["1.0.0"], tag_name="version"),
                    "filename": s_name + ".sld",
                    }
                }

    @HTTPCompatible()
    def PUT(self, map_name, s_name, format):
        path = tools.get_style_path(s_name)
        try:
            os.remove(path)
        except OSError:
            mf = get_mapfile(map_name)
            if s_name in mf.iter_styles():
                raise webapp.NotImplemented(message="Updating manually added styles is not implemented.")
            else:
                raise webapp.NotFound("style '%s' not found in mapfile '%s'." % (s_name, map_name))

        data = web.data()
        with open(path, "w") as f:
            f.write(data)


    @HTTPCompatible()
    def DELETE(self, map_name, s_name, format):
        mf = get_mapfile(map_name)

        # OK check any(class.group == s_name for class in layer.iter_classes)
        layers_using = [layer.ms.name for layer in mf.iter_layers()
                        if any(clazz.ms.group == s_name for clazz in layer.iter_classes())]

        if layers_using:
            raise webapp.Forbidden(message="Can't remove style '%s' because it is beeing used by the folowing layers: %s."
                                   % (s_name, layers_using))

        path = tools.get_style_path(s_name)
        try:
            os.remove(path)
        except OSError:
            mf = get_mapfile(map_name)
            if s_name in mf.iter_styles():
                raise webapp.NotImplemented(message="Deleting manually added styles is not implemented.")
            else:
                raise webapp.NotFound("style '%s' not found in mapfile '%s'." % (s_name, map_name))


class layers(object):
    @HTTPCompatible()
    def GET(self, map_name, format):
        mf = get_mapfile(map_name)
        return {"layers": [{
                    "name": layer.ms.name,
                    "href": "%s/maps/%s/layers/%s.%s" % (web.ctx.home, map_name, layer.ms.name, format),
                    } for layer in mf.iter_layers()]
                }

    @HTTPCompatible()
    def POST(self, map_name, format):
        data = get_data(name="layer",
                        mandatory=["name", "resource"],
                        authorized=["name", "title", "abstract", "resource", "enabled"])

        l_name = data.pop("name")
        l_enabled = data.pop("enabled", True)

        # This means we can have one mapfile for each workspace
        # and if eveything uses urls it should work *almost* as is.
        url = urlparse.urlparse(data["resource"]["href"])
        if url.path.startswith(web.ctx.homepath):
            path = url.path[len(web.ctx.homepath):]
        else:
            raise webapp.BadRequest(message="Resource href is not handled by MRA.")

        try:
            _, map_name, _, ws_name, st_type, st_name, r_type, r_name = path.rsplit("/", 7)
        except ValueError:
            raise webapp.NotFound(message="ressource '%s' was not found." % path)

        r_name = r_name.rsplit(".", 1)[0]

        mf, ws = get_mapfile_workspace(map_name, ws_name)
        with webapp.mightNotFound(r_type, workspace=ws_name):
            try:
                model = ws.get_model(r_name, r_type[:-1], st_name)
            except ValueError:
                webapp.NotFound("Invalid layer model '%s'" % r_type[:-1])

        with webapp.mightConflict("layer", mapfile=map_name):
            mf.create_layer(ws, model, l_name, l_enabled)
        mf.save()

        webapp.Created("%s/maps/%s/layers/%s%s" % (web.ctx.home, map_name, l_name, (".%s" % format) if format else ""))


class layer(object):
    @HTTPCompatible()
    def GET(self, map_name, l_name, format):
        mf = get_mapfile(map_name)
        with webapp.mightNotFound("layer", mapfile=map_name):
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
                        "href": "%s/maps/%s/styles/%s.%s" % (web.ctx.home, map_name, layer.ms.classgroup, format),
                        },
                    "styles": [{ # TODO: Add attr class="linked-hash-set"
                            "name": s_name,
                            "href": "%s/maps/%s/styles/%s.%s" % (web.ctx.home, map_name, s_name, format),
                            } for s_name in layer.iter_styles()],
                    "resource": { # TODO: Add attr class="featureType|coverage"
                        "name": layer.get_mra_metadata("name"),
                        "href": "%s/maps/%s/workspaces/%s/%ss/%s/%ss/%s.%s" % (
                            web.ctx.home, map_name, layer.get_mra_metadata("workspace"),
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
    def PUT(self, map_name, l_name, format):
        mf = get_mapfile(map_name)

        data = get_data(name="layer", mandatory=["name", "resource"],
                        authorized=["name", "title", "abstract", "resource", "enabled"])
        if l_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a layer.")

        l_enabled = data.pop("enabled", True)

        # This means we can have one mapfile for each workspace
        # and if eveything uses urls it should work *almost* as is.
        r_href = data["resource"]["href"]
        try:
            _, map_name, _, ws_name, st_type, st_name, r_type, r_name = r_href.rsplit("/", 7)
        except ValueError:
            raise webapp.NotFound(message="ressource '%s' was not found." % r_href)

        r_name = r_name.rsplit(".", 1)[0]

        ws = mf.get_workspace(ws_name)
        with webapp.mightNotFound(r_type, workspace=ws_name):
            try:
                model = ws.get_model(r_name, r_type[:-1], st_name)
            except ValueError:
                raise webapp.NotFound("Invalid layer model '%s'" % st_type)

        with webapp.mightNotFound("layer", mapfile=map_name):
            layer = mf.get_layer(l_name)

            if layer.get_mra_metadata("type") != r_type:
                raise webapp.BadRequest("Can't change a '%s' layer into a '%s'." % (
                        layer.get_mra_metadata("type"), r_type))

            model.configure_layer(ws, layer, l_enabled)
        mf.save()

    @HTTPCompatible()
    def DELETE(self, map_name, l_name, format):
        mf = get_mapfile(map_name)
        with webapp.mightNotFound("layer", mapfile=map_name):
            mf.delete_layer(l_name)
        mf.save()


class layerstyles(object):
    @HTTPCompatible()
    def GET(self, map_name, l_name, format):
        mf = get_mapfile(map_name)
        with webapp.mightNotFound("layer", mapfile=map_name):
            layer = mf.get_layer(l_name)

        if format == "sld":
            return layer.getSLD()

        return {"styles": [{
                    "name": s_name,
                    "href": "%s/maps/%s/styles/%s.%s" % (web.ctx.home, map_name, s_name, format),
                    } for s_name in layer.iter_styles()],
                }

    @HTTPCompatible()
    def POST(self, map_name, l_name, format):
        data = get_data(name="style", mandatory=["resource"],
                        authorized=["name", "title", "abstract", "resource"])

        url = urlparse.urlparse(data["resource"]["href"])
        if url.path.startswith(web.ctx.homepath):
            path = url.path[len(web.ctx.homepath):]
        else:
            raise webapp.BadRequest(message="Resource href (%s) is not handled by MRA." % url.path)

        try:
            _, map_name, _, s_name = path.rsplit("/", 3)
        except ValueError:
            raise webapp.NotFound(message="ressource '%s' was not found." % path)

        s_name = s_name.rsplit(".", 1)[0]

        # Get the new style.
        mf = get_mapfile(map_name)

        try:
            style = open(tools.get_style_path(s_name)).read()
        except IOError, OSError:
            with webapp.mightNotFound("style", mapfile=map_name):
                style = mf.get_style_sld(s_name)

        with webapp.mightNotFound("layer", mapfile=map_name):
            layer = mf.get_layer(l_name)

        layer.add_style_sld(mf, s_name, style)
        mf.save()

        webapp.Created("%s/maps/%s/layers/%s/layerstyles/%s%s" % (web.ctx.home, map_name, l_name, s_name, (".%s" % format) if format else ""))


class layerstyle(object):
    @HTTPCompatible()
    def DELETE(self, map_name, l_name, s_name, format):
        mf = get_mapfile(map_name)
        with webapp.mightNotFound("layer", mapfile=map_name):
            layer = mf.get_layer(l_name)
        with webapp.mightNotFound("style", layer=l_name):
            layer.remove_style(s_name)
        mf.save()


class layerfields(object):
    @HTTPCompatible()
    def GET(self, map_name, l_name, format):
        mf = get_mapfile(map_name)
        with webapp.mightNotFound("layer", mapfile=map_name):
            layer = mf.get_layer(l_name)

            return {"fields": [{
                    "name": layer.get_metadata("gml_%s_alias" % field, None),
                    "fieldType": layer.get_metadata("gml_%s_type" % field, None),
                    } for field in layer.iter_fields()]
                }


class layergroups(object):
    @HTTPCompatible()
    def GET(self, map_name, format):
        mf = get_mapfile(map_name)

        return {"layerGroups" : [{
                    "name": lg.name,
                    "href": "%s/maps/%s/layergroups/%s.%s" % (web.ctx.home, map_name, lg.name, format)
                    } for lg in mf.iter_layergroups()]
                }

    @HTTPCompatible()
    def POST(self, map_name, format):
        mf = get_mapfile(map_name)

        data = get_data(name="layerGroup", mandatory=["name"], authorized=["name", "title", "abstract", "layers"])
        lg_name = data.pop("name")
        layers = [mf.get_layer(l_name) for l_name in data.pop("layers", [])]

        with webapp.mightConflict("layerGroup", mapfile=map_name):
            lg = mf.create_layergroup(lg_name, data)
        lg.add(*layers)

        mf.save()

        webapp.Created("%s/maps/%s/layergroups/%s%s" % (web.ctx.home, map_name, lg.name, (".%s" % format) if format else ""))


class layergroup(object):

    @HTTPCompatible()
    def GET(self, map_name, lg_name, format):
        mf = get_mapfile(map_name)
        with webapp.mightNotFound("layerGroup", mapfile=map_name):
            lg = mf.get_layergroup(lg_name)

        latlon_extent = lg.get_latlon_extent()

        return {"layerGroup": ({
                    "name": lg.name,
                    "mode": None, # TODO
                    "publishables": [{
                            "name": layer.ms.name,
                            "href": "%s/maps/%s/layers/%s.%s" % (web.ctx.home, map_name, layer.ms.name, format),
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
    def PUT(self, map_name, lg_name, format):
        mf = get_mapfile(map_name)

        with webapp.mightNotFound("layerGroup", mapfile=map_name):
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
    def DELETE(self, map_name, lg_name, format):

        mf = get_mapfile(map_name)
        with webapp.mightNotFound("layerGroup", mapfile=map_name):
            mf.delete_layergroup(lg_name)
        mf.save()


# Index:
urlmap(index, "")

# Mapfiles:
urlmap(mapfiles, "maps")
urlmap(named_mapfile, "maps", ())

# Workspaces:
urlmap(workspaces, "maps", (), "workspaces")
urlmap(workspace, "maps", (), "workspaces", ())

# Datastores:
urlmap(datastores, "maps", (), "workspaces", (), "datastores")
urlmap(datastore, "maps", (), "workspaces", (), "datastores", ())
# Featuretypes:
urlmap(featuretypes, "maps", (), "workspaces", (), "datastores", (), "featuretypes")
urlmap(featuretype, "maps", (), "workspaces", (), "datastores", (), "featuretypes", ())

# Coveragestores:
urlmap(coveragestores, "maps", (), "workspaces", (), "coveragestores")
urlmap(coveragestore, "maps", (), "workspaces", (), "coveragestores", ())
# Coverages:
urlmap(coverages, "maps", (), "workspaces", (), "coveragestores", (), "coverages")
urlmap(coverage, "maps", (), "workspaces", (), "coveragestores", (), "coverages", ())

# Files:
urlmap(files, "maps", (), "workspaces", (), "(datastores|coveragestores)", (), "(file|url|external)")

# Styles:
urlmap(styles, "maps", (), "styles")
urlmap(style, "maps", (), "styles", ())

# Layers, layer styles and data fields:
urlmap(layers, "maps", (), "layers")
urlmap(layer, "maps", (), "layers", ())
urlmap(layerstyles, "maps", (), "layers", (), "styles")
urlmap(layerstyle, "maps", (), "layers", (), "styles", ())
urlmap(layerfields, "maps", (), "layers", (), "fields")

# Layergroups:
urlmap(layergroups, "maps", (), "layergroups")
urlmap(layergroup, "maps", (), "layergroups", ())

urls = tuple(urlmap)

web.config.debug = get_config("debug").get("web_debug", False)
webapp.exceptionManager.raise_all = get_config("debug").get("raise_all", False)
HTTPCompatible.return_logs = get_config("logging").get("web_logs", False)

for pdir in get_config("plugins").get("loadpaths", []):
    plugins.load_plugins_dir(pdir)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()

application = app.wsgifunc()
