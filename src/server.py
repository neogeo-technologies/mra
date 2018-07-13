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
    URL mapping infrastructure and HTTP methods used by the REST API.


"""

import os.path
import sys
import web
import json
import urlparse
import logging
import mralogs
from mra import MRA
import webapp
from webapp import HTTPCompatible, urlmap, get_data
import tools
from tools import href, assert_is_empty
from pyxml import Entries
from extensions import plugins
import mapscript


# Some helper functions first.


def get_workspace(ws_name):
    with webapp.mightNotFound():
        return mra.get_workspace(ws_name)


# Now the main classes that handle the REST API.


class index(object):
    """Index of the API (e.g. http://hostname/mra/)

    """
    @HTTPCompatible(authorized=["html"])
    def GET(self, format):
        return {
            "about/version": href("about/version"),
            "workspaces": href("workspaces"),
            "styles": href("styles"),
            "layers": href("layers"),
            "layergroups": href("layergroups"),
            "services/wms/settings": href("services/wms/settings"),
            "services/wcs/settings": href("services/wcs/settings"),
            "services/wfs/settings": href("services/wfs/settings"),
            "fonts": href("fonts"),
            }


class version(object):
    """To know about used versions...

    """
    @HTTPCompatible()
    def GET(self, format):
        return {"about": {"resources": [
                        {"name": "MapServer", "version": tools.ms_version()},
                        {"name": "GDAL", "version": tools.gdal_version()},
                    ]}
                }


class workspaces(object):
    """Workspaces container.

    http://hostname/mra/workspaces

    See 'workspace' class documentation for definition of a 'workspace'.

    """
    @HTTPCompatible()
    def GET(self, format, *args, **kwargs):
        """List all workspaces."""

        return {"workspaces": [{
                    "name": ws_name,
                    "href": "%s/workspaces/%s.%s" % (web.ctx.home, ws_name, format)
                    } for ws_name in mra.list_workspaces()]
                }

    @HTTPCompatible()
    def POST(self, format):
        """Create a new workspace."""

        data = get_data(name="workspace", mandatory=["name"], authorized=["name"])
        ws_name = data.pop("name")

        with webapp.mightConflict():
            mra.create_workspace(ws_name).save()
            # TODO Create associated service

        webapp.Created("%s/workspaces/%s.%s" % (web.ctx.home, ws_name, format))


class workspace(object):
    """A workspace is a grouping of data stores and coverage stores.

    http://hostname/mra/workspaces/<ws>

    In fact, a workspace is assimilated to one mapfile (<workspace_name>.ws.map)
    which contains some unactivated layers. These layers allows to configure
    connections to data (data store or coverage store) then data
    itself (featuretype for vector type or coverage for raster type).

    These layers should not be published as OGC service as such.
    However, in the near future (TODO), it should be possible to publish
    a workspace as permitted GeoServer.
    And this workspace should be identified as a usual MapFile.

    """
    @HTTPCompatible()
    def GET(self, ws_name, format):
        """Return workspace <ws>."""

        ws = get_workspace(ws_name)
        return {"workspace": ({
                    "name": ws.name,
                    "dataStores":
                        href("%s/workspaces/%s/datastores.%s" % (web.ctx.home, ws.name, format)),
                    "coverageStores":
                        href("%s/workspaces/%s/coveragestores.%s" % (web.ctx.home, ws.name, format)),
                    })
                }

    # TODO: def PUT(...
    # TODO: def DELETE(...


class datastores(object):
    """Data stores container.

    http://hostname/mra/workspaces/<ws>/datastores

    See 'datastore' class documentation for definition of a 'datastore'.

    """
    @HTTPCompatible()
    def GET(self, ws_name, format):
        """List all data stores in workspace <ws>."""

        ws = get_workspace(ws_name)
        return {"dataStores": [{
                    "name": ds_name,
                    "href": "%s/workspaces/%s/datastores/%s.%s" % (
                        web.ctx.home, ws.name, ds_name, format)
                    } for ds_name in ws.iter_datastore_names()]
                }

    @HTTPCompatible()
    def POST(self, ws_name, format):
        """Create a new data store."""

        ws = get_workspace(ws_name)

        data = get_data(name="dataStore", mandatory=["name"],
                        authorized=["name", "title", "abstract", "connectionParameters"])
        ds_name = data.pop("name")

        with webapp.mightConflict("dataStore", workspace=ws_name):
            ws.create_datastore(ds_name, data)

        ws.save()

        webapp.Created("%s/workspaces/%s/datastores/%s.%s" % (
            web.ctx.home, ws_name, ds_name, format))


class datastore(object):
    """A data store is a source of spatial data that is vector based.

    http://hostname/mra/workspaces/<ws>/datastores/<ds>

    A data store is a connection to a data source as implied by OGR library.
    It could be a shapefile, a PostGIS database or any other data type supported by OGR.

    """
    @HTTPCompatible()
    def GET(self, ws_name, ds_name, format):
        """Return data store <ds>."""

        ws = get_workspace(ws_name)

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            info = ws.get_datastore_info(ds_name)
        connectionParameters = info.get("connectionParameters", {})

        return {"dataStore": {
                    "name": info["name"],
                    "enabled": True,  # Always enabled
                                      # TODO: Handle enabled/disabled states
                    "workspace": {
                        "name": ws.name,
                        "href": "%s/workspaces/%s.%s" % (
                            web.ctx.home, ws.name, format),
                        },
                    "featureTypes": href("%s/workspaces/%s/datastores/%s/featuretypes.%s" % (
                                        web.ctx.home, ws.name, ds_name, format)
                        ),
                    "connectionParameters": Entries(connectionParameters, tag_name="entry"),
                    }
                }

    @HTTPCompatible()
    def PUT(self, ws_name, ds_name, format):
        """Modify data store <ds>."""

        ws = get_workspace(ws_name)

        data = get_data(name="dataStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])

        if ds_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a data store.")

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            ws.update_datastore(ds_name, data)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, ws_name, ds_name, format):
        """Delete data store <ds>."""

        ws = get_workspace(ws_name)

        # TODO: check, this is not consistent between ds/cs.
        # We need to check if this datastore is empty.
        assert_is_empty(ws.iter_featuretypemodels(ds_name=ds_name), "datastore", ds_name)

        with webapp.mightNotFound("dataStore", workspace=ws_name):
            ws.delete_datastore(ds_name)
        ws.save()


class featuretypes(object):
    """Feature types container.

    http://hostname/mra/workspaces/<ws>/datastores/<ds>/featuretypes

    See 'featuretype' class documentation for definition of a 'featuretype'.

    """
    @HTTPCompatible()
    def GET(self, ws_name, ds_name, format):
        """List all feature types in selected data store <ds>."""

        ws = get_workspace(ws_name)
        return {"featureTypes": [{
                    "name": ft.name,
                    "href": "%s/workspaces/%s/datastores/%s/featuretypes/%s.%s" % (
                        web.ctx.home, ws.name, ds_name, ft.name, format)
                    } for ft in ws.iter_featuretypemodels(ds_name)]
                }

    @HTTPCompatible()
    def POST(self, ws_name, ds_name, format):
        """Create a new feature type. It create the associated layer by defaut.
        This layer is added in the mapfile: <layer.map>

        """
        ws = get_workspace(ws_name)
        data = get_data(name="featureType", mandatory=["name"],
                        authorized=["name", "title", "abstract", "enabled"])

        l_enabled = data.pop("enabled", True)

        # Creates first the feature type:
        with webapp.mightConflict("featureType", datastore=ds_name):
            with webapp.mightNotFound("featureType", datastore=ds_name):
                ws.create_featuretypemodel(ds_name, data["name"], data)
        ws.save()

        # Then creates the associated layer by default:
        #   - in layers.map
        model = ws.get_featuretypemodel(ds_name, data["name"])
        mf = mra.get_available()
        with webapp.mightConflict():
            mf.create_layer(model, data["name"], l_enabled)
        mf.save()

        #   - in {workspace}.map
        wsmf = mra.get_service(ws_name)
        with webapp.mightConflict():
            wsmf.create_layer(model, data["name"], l_enabled)
        wsmf.save()

        webapp.Created("%s/workspaces/%s/datastores/%s/featuretypes/%s.%s" % (
                web.ctx.home, ws.name, ds_name, data["name"], format))


class featuretype(object):
    """A feature type is a data set that originates from a data store.

    http://hostname/mra/workspaces/<ws>/datastores/<ds>/featuretypes/<ft>

    A feature type is considered as a layer under MapServer which is still unactivated.

    """
    @HTTPCompatible()
    def GET(self, ws_name, ds_name, ft_name, format):
        """Return feature type <ft>."""

        ws = get_workspace(ws_name)

        ds = ws.get_datastore(ds_name)

        with webapp.mightNotFound("dataStore", datastore=ds_name):
            dsft = ds[ft_name]

        with webapp.mightNotFound("featureType", datastore=ds_name):
            ft = ws.get_featuretypemodel(ds_name, ft_name)

        extent = ft.get_extent()
        latlon_extent = ft.get_latlon_extent()


        # About attributs, we apply just values handled by
        # MapServer in a GetFeature response...
        attributes = [{
            "name": f.get_name(),
            "type": f.get_type_name(),
            "length": f.get_width(),
            # "minOccurs": 0, "maxOccurs": 1, "nillable": f.is_nullable(),
            # binding?
            } for f in dsft.iterfields()]

        if dsft.get_geometry_column() is not None:
            attributes.append({
                "name": dsft.get_geometry_column(),
                "type": dsft.get_geomtype_gml(),
                "minOccurs": 0,
                "maxOccurs": 1,
                # "nillable": True,
                # binding?
                })
        else:
            attributes.append({
                "name": "geometry",
                "type": dsft.get_geomtype_gml(),
                "minOccurs": 0,
                "maxOccurs": 1,
                # "nillable": True,
                # binding?
                })

        return {"featureType": ({
                    # Why the name would it be different from nativeName?
                    "name": ft.name,
                    "nativeName": ft.name,
                    "title": ft.get_mra_metadata("title", ft.name),
                    "abstract": ft.get_mra_metadata("abstract", None),
                    # TODO: keywords
                    "nativeCRS": ft.get_wkt(),
                    "attributes": attributes,
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
                    # "srs": "%s:%s" % (ft.get_authority()[0], ft.get_authority()[1]),
                    "projectionPolicy": "NONE",
                    # About srs & projectionPolicy: (TODO: Handle the other cases)
                    # In MRA, it is easier (or more logical?) to keep native CRS,
                    # Or there is a problem of understanding on our part.
                    # So, i prefer to comment 'srs' entry cause we force the
                    # value of 'projectionPolicy' to 'NONE'... but it is something
                    # we should investigate...
                    "enabled": True,  # Always enabled => TODO
                    "store": {  # TODO: add key: class="dataStore"
                        "name": ds_name,
                        "href": "%s/workspaces/%s/datastores/%s.%s" % (
                            web.ctx.home, ws_name, ds_name, format)
                        },
                    # TODO: maxFeatures
                    })
                }

    @HTTPCompatible()
    def PUT(self, ws_name, ds_name, ft_name, format):
        """Modify feature type <ft>."""

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
        """Delete feature type <ft>."""

        ws = get_workspace(ws_name)

        # We need to check if there are any layers using this.
        mf = mra.get_available()
        assert_is_empty(mf.iter_layers(mra={"name":ft_name, "workspace":ws_name, "storage":ds_name,
                                            "type":"featuretype"}),"featuretype", ft_name)

        with webapp.mightNotFound("featureType", datastore=ds_name):
            ws.delete_featuretypemodel(ds_name, ft_name)
        ws.save()


class coveragestores(object):
    """Coverage stores container.

    http://hostname/mra/workspaces/<ws>/coveragestores

    See 'coveragestore' class documentation for definition of a 'coveragestore'.

    """
    @HTTPCompatible()
    def GET(self, ws_name, format):
        """List all coverage stores in workspace."""

        ws = get_workspace(ws_name)
        return {"coverageStores": [{
                    "name": cs_name,
                    "href": "%s/workspaces/%s/coveragestores/%s.%s" % (
                        web.ctx.home, ws.name, cs_name, format)
                    } for cs_name in ws.iter_coveragestore_names()]
                }

    @HTTPCompatible()
    def POST(self, ws_name, format):
        """Create new coverage store."""

        ws = get_workspace(ws_name)
        data = get_data(name="coverageStore", mandatory=["name"], authorized=["name", "title", "abstract", "connectionParameters"])
        cs_name = data.pop("name")

        with webapp.mightConflict("coverageStore", workspace=ws_name):
            ws.create_coveragestore(cs_name, data)
        ws.save()

        # Then creates the associated layer by default:
        # model = ws.get_coveragetypemodel(cs_name, data["name"])
        # mf = mra.get_available()
        # with webapp.mightConflict():
        #     mf.create_layer(model, data["name"], True)
        # mf.save()

        webapp.Created("%s/workspaces/%s/coveragestores/%s.%s" % (
                web.ctx.home, ws_name, cs_name, format))


class coveragestore(object):
    """A coverage store is a source of spatial data that is raster based.

    http://hostname/mra/workspaces/<ws>/coveragestores/<cs>

    A coverage store is a connection to a raster data source as implied by GDAL library.

    """
    @HTTPCompatible()
    def GET(self, ws_name, cs_name, format):
        """Return coverage store <cs>."""

        ws = get_workspace(ws_name)
        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            info = ws.get_coveragestore_info(cs_name)
        connectionParameters = info.get("connectionParameters", {})

        return {"coverageStore": {
                    "name": info["name"],
                    "enabled": True, # Always enabled
                                     # TODO: Handle enabled/disabled states
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
                        # "namespace": None, # TODO
                        }, tag_name="entry"),
                    # TODO: type
                    }
                }

    @HTTPCompatible()
    def PUT(self, ws_name, cs_name, format):
        """Modify coverage store <ds>."""

        ws = get_workspace(ws_name)
        data = get_data(name="coverageStore",
                        mandatory=["name"],
                        authorized=["name", "title", "abstract", "connectionParameters"])
        if cs_name != data.pop("name"):
            raise webapp.Forbidden("Can't change the name of a coverage store.")

        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            ws.update_coveragestore(cs_name, data)
        ws.save()

    @HTTPCompatible()
    def DELETE(self, ws_name, cs_name, format):
        """Delete coverage store <cs>."""

        ws = get_workspace(ws_name)
        # TODO: check, this is not consistent between ds/cs.
        # We need to check if this datastore is empty.
        assert_is_empty(ws.iter_coveragemodels(cs_name=cs_name), "coveragestore", cs_name)

        with webapp.mightNotFound("coverageStore", workspace=ws_name):
            ws.delete_coveragestore(cs_name)
        ws.save()


class coverages(object):
    """Coverages container.

    http://hostname/mra/workspaces/<ws>/coveragestores/<cs>/coverage

    See 'coverage' class documentation for definition of a 'coverage'.

    """
    @HTTPCompatible()
    def GET(self, ws_name, cs_name, format):
        """List all coverages in selected coverages store <cs>."""

        ws = get_workspace(ws_name)
        return {"coverages": [{
                    "name": c.name,
                    "href": "%s/workspaces/%s/coveragestores/%s/coverages/%s.%s" % (
                        web.ctx.home, ws.name, cs_name, c.name, format)
                    } for c in ws.iter_coveragemodels(cs_name)]
                }

    @HTTPCompatible()
    def POST(self, ws_name, cs_name, format):
        """Create a new coverage."""

        ws = get_workspace(ws_name)
        data = get_data(name="coverage", mandatory=["name"], authorized=["name", "title", "abstract"])
        with webapp.mightConflict("coverage", coveragestore=cs_name):
            with webapp.mightNotFound("coverage", coveragestore=cs_name):
                ws.create_coveragemodel(data["name"], cs_name, data)
        ws.save()

        # Then creates the associated layer by default:
        model = ws.get_coveragemodel(cs_name, data["name"])
        mf = mra.get_available()
        with webapp.mightConflict():
            mf.create_layer(model, data["name"], True)
        mf.save()

        webapp.Created("%s/workspaces/%s/coveragestores/%s/coverages/%s.%s" % (
                web.ctx.home, ws.name, cs_name, data["name"], format))


class coverage(object):
    """A coverage is a raster based data set that originates from a coverage store.

    http://hostname/mra/workspaces/<ws>/coveragestores/<cs>/coverage/<c>

    A coverage is considered as a layer under MapServer which is still unactivated.

    """
    @HTTPCompatible()
    def GET(self, ws_name, cs_name, c_name, format):
        """Return coverage <c>."""

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
                    "title": c.get_mra_metadata("title", c.name),
                    "abstract": c.get_mra_metadata("abstract", None),
                    # TODO: Keywords
                    "nativeCRS": c.get_wkt(),  # TODO: Add key class="projected" if projected...
                    "srs": "%s:%s" % (c.get_authority_name(), c.get_authority_code()),
                    "nativeBoundingBox": {
                        "minx": extent.minX(),
                        "miny": extent.minY(),
                        "maxx": extent.maxX(),
                        "maxy": extent.maxY(),
                        "crs": "%s:%s" % (c.get_authority_name(), c.get_authority_code()),  # TODO: Add key class="projected" if projected...
                        },
                    "latLonBoundingBox":{
                        "minx": latlon_extent.minX(),
                        "miny": latlon_extent.minY(),
                        "maxx": latlon_extent.maxX(),
                        "maxy": latlon_extent.maxY(),
                        "crs": "EPSG:4326"
                        },
                    "enabled": True,  # Always enabled => TODO
                    "store": {  # TODO: Add attr class="coverageStore"
                        "name": cs_name,
                        "href": "%s/workspaces/%s/coveragestores/%s.%s" % (
                            web.ctx.home, ws_name, cs_name, format)
                        },
                    # TODO:
                    # "nativeFormat": None,
                    # "grid": {
                    #     "range": {
                    #         "low": None,
                    #         "high": None,
                    #         },
                    #     "transform": {
                    #         "scaleX": None,
                    #         "scaleY": None,
                    #         "shearX": None,
                    #         "shearY": None,
                    #         "translateX": None,
                    #         "translateY": None,
                    #         },
                    #     "crs": None,
                    #     },
                    # "supportedFormats": [],
                    # "interpolationMethods": [],
                    # "defaultInterpolationMethod": None,
                    # "dimensions": [],
                    # "projectionPolicy": None,
                    # "requestSRS": None,
                    # "responseSRS": None,
                    # "parameters": None,
                    })
                }

    @HTTPCompatible()
    def PUT(self, ws_name, cs_name, c_name, format):
        """Modify coverage <c>."""

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
        """Delete coverage <c>."""

        ws = get_workspace(ws_name)
        # We need to check if there are any layers using this.
        mf = mra.get_available()
        assert_is_empty(mf.iter_layers(mra={"name":c_name, "workspace":ws_name, "storage":cs_name,
                                            "type":"coverage"}), "coverage", c_name)

        with webapp.mightNotFound("coverage", coveragestore=cs_name):
            ws.delete_coveragemodel(c_name, cs_name)
        ws.save()


class files(object):
    """
    http://hostname/mra/workspaces/<ws>/datastores/<cs>/file.<extension>

    http://hostname/mra/workspaces/<ws>/coveragestores/<cs>/file.<extension>

    """
    @HTTPCompatible(allow_all=True)
    def PUT(self, ws_name, st_type, st_name, f_type, format):
        """Uploads a file from a local source. The body of the request is the file itself."""

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
                st_type = st_type[:-1]  # Remove trailing 's'
                with webapp.mightConflict("Workspace", workspace=ws_name):
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
        ws.update_store(st_type, st_name, {
            "connectionParameters": {"url": "file:" + mra.pub_file_path(path)}})
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


class fonts(object):
    """Configure available fonts.

    http://hostname/mra/fonts

    """
    @HTTPCompatible()
    def GET(self, format):
        """Returns the list of available fonts."""

        return {"fonts": [f_name for f_name in mra.list_fontset()]}

    @HTTPCompatible()
    def PUT(self, format):
        """Uploads fonts from a local source."""

        import zipfile
        ctype = web.ctx.env.get("CONTENT_TYPE", None)
        if ctype == "application/zip":
            path = mra.create_font("archive.zip", data=web.data())
            with zipfile.ZipFile(path, "r") as z:
                z.extractall(mra.get_font_path())
            os.remove(path)

        mra.update_fontset()

        # Then updates (the) mapfile(s) only
        # if the fontset path is not specified.
        # Should it be done here ?...
        mf = mra.get_available()
        if mf.ms.fontset.filename is None:
            mf.ms.setFontSet(mra.get_fontset_path())
            mf.save()


class styles(object):
    """SLD styles container.

    http://hostname/mra/styles

    """
    @HTTPCompatible()
    def GET(self, format):
        """List all SLD styles."""

        return {"styles": [{
                    "name": s_name,
                    "href": "%s/styles/%s.%s" % (web.ctx.home, s_name, format)
                    } for s_name in mra.list_styles()]
                }

    @HTTPCompatible(authorize=["sld"])
    def POST(self, format):
        """Create a new SLD style. Add the 'name' parameter in order to specify
        the name to be given to the new style.

        """
        params = web.input(name=None)
        name = params.name
        if name is None:
            raise webapp.BadRequest(message="no parameter \"name\" given.")

        data = web.data()
        mra.create_style(name, data)

        webapp.Created("%s/styles/%s.%s" % (web.ctx.home, name, format))


class style(object):
    """A style describes how a resource (a feature type or a coverage) should be
    symbolized or rendered by a Web Map Service.

    http://hostname/mra/styles/<s>

    Styles are specified with SLD and translated into the mapfile (with CLASS and
    STYLE blocs) to be applied.
    An extension may be considered to manage all style possibilities offered by MapServer.
    This should be made with the module 'extensions.py'.

    """
    @HTTPCompatible(authorize=["sld"])
    def GET(self, s_name, format):
        """Return style <s>."""

        with webapp.mightNotFound(message="Style \"%s\" does not exist." % s_name):
            style = mra.get_style(s_name)

        if format == "sld":
            return style

        return {"style": {
                    "name": s_name,
                    "sldVersion": Entries(["1.0.0"], tag_name="version"),
                    "filename": s_name + ".sld",
                    }
                }

    @HTTPCompatible(authorize=["sld"])
    def PUT(self, s_name, format):
        """Modify style <s>."""

        # TODO: Also update layers using this style.
        with webapp.mightNotFound(message="Style \"%s\" does not exist." % s_name):
            mra.delete_style(s_name)
        data = web.data()
        mra.create_style(s_name, data)

    # TODO: def DELETE(...


class layers(object):
    """Layers container.

    http://hostname/mra/layers

    """
    @HTTPCompatible()
    def GET(self, format):
        """List all layers."""

        mf = mra.get_available()
        return {"layers": [{
                    "name": layer.ms.name,
                    "href": "%s/layers/%s.%s" % (web.ctx.home, layer.ms.name, format),
                    } for layer in mf.iter_layers()]
                }

    @HTTPCompatible()
    def POST(self, format):
        """Create a new layer."""

        data = get_data(name="layer",
                        mandatory=["name", "resource"],
                        authorized=["name", "title", "abstract", "resource", "enabled", "defaultStyle"])

        l_name = data.pop("name")
        l_enabled = data.pop("enabled", True)

        href = data["resource"]["href"]
        try:
            ws_name, st_type, st_name, r_type, r_name = mra.href_parse(href, 5)
        except ValueError:
            raise webapp.NotFound(message="resource \"%s\" was not found." % href)

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

        wsmf = mra.get_service(ws_name)
        with webapp.mightConflict():
            wsmf.create_layer(model, l_name, l_enabled)

        # If we have a defaultStyle apply it.
        s_name = data.get("defaultStyle", {}).get("name")
        if s_name:
            with webapp.mightNotFound():
                style = mra.get_style(s_name)
                layer = mf.get_layer(l_name)
                wslayer = wsmf.get_layer(l_name)
            layer.add_style_sld(mf, s_name, style)
            wslayer.add_style_sld(wsmf, s_name, style)

            # Remove the automatic default style.
            for s_name in layer.iter_styles():
                if s_name == tools.get_dflt_sld_name(layer.ms.type):
                    layer.remove_style(s_name)

            for s_name in wslayer.iter_styles():
                if s_name == tools.get_dflt_sld_name(wslayer.ms.type):
                    wslayer.remove_style(s_name)

        mf.save()
        wsmf.save()

        webapp.Created("%s/layers/%s.%s" % (web.ctx.home, l_name, format))


class layer(object):
    """A layer is a published resource (feature type or coverage) from a MapFile.

    http://hostname/mra/layers/<l>

    All layers are added in one single MapFile which should be activate as OGC service.

    """
    @HTTPCompatible()
    def GET(self, l_name, format):
        """Return layer <l>."""

        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)

        data_type, store_type = {
            "featuretype": ("featuretype", "datastore"),
            "coverage": ("coverage", "coveragestore")
            }[layer.get_mra_metadata("type")]

        response = {"layer": {
                    "name": l_name,
                    "title": layer.get_metadata("ows_title", None),
                    "abstract": layer.get_metadata("ows_abstract", None),
                    "type": layer.get_type_name(),
                    "resource": {
                        # TODO: Add attr class="featureType|coverage"
                        "name": layer.get_mra_metadata("name"),
                        "href": "%s/workspaces/%s/%ss/%s/%ss/%s.%s" % (
                            web.ctx.home, layer.get_mra_metadata("workspace"),
                            store_type, layer.get_mra_metadata("storage"),
                            data_type, layer.get_mra_metadata("name"), format),
                        },
                    "enabled": bool(layer.ms.status),  # TODO because it's fictitious...
                    # "attribution" => TODO?
                    # "path" => TODO?
                    }}

        # Check CLASSGROUP
        dflt_style = layer.ms.classgroup
        if dflt_style is None:
            # If is 'None': take the first style as would MapServer.
            for s_name in layer.iter_styles():
                dflt_style = s_name
                break
        if dflt_style is None:
            return response

        response["layer"].update({
            "defaultStyle": {
                "name": dflt_style,
                "href": "%s/styles/%s.%s" % (web.ctx.home, dflt_style, format)
                }
            })

        styles = [{"name": s_name,
                   "href": "%s/styles/%s.%s" % (web.ctx.home, s_name, format),
                   } for s_name in layer.iter_styles() if s_name != dflt_style]
        if not styles:
            return response

        return response["layer"].update({"styles": styles})

    @HTTPCompatible()
    def PUT(self, l_name, format):
        """Modify layer <l>."""

        mf = mra.get_available()

        data = get_data(name="layer", mandatory=[],
                        authorized=["name", "resource", "defaultStyle",
                                    "title", "type", "enabled", "href", "abstract"])
        if l_name != data.get("name", l_name):
            raise webapp.Forbidden("Can't change the name of a layer.")

        l_enabled = data.pop("enabled", True)

        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)

        ws_name = layer.get_mra_metadata('workspace')
        wsmf = mra.get_service(ws_name)
        with webapp.mightConflict():
            wslayer = wsmf.get_layer(l_name)

        layer.enable(l_enabled)
        wslayer.enable(l_enabled)

        # update resource if changed
        href = data.get("resource", {}).get("href")
        if href:
            try:
                ws_name, st_type, st_name, r_type, r_name = mra.href_parse(href, 5)
            except ValueError:
                raise webapp.NotFound(message="resource \"%s\" was not found." % href)

            st_type, r_type = st_type[:-1], r_type[:-1]  # Remove trailing s.

            ws = get_workspace(ws_name)
            with webapp.mightNotFound(r_type, workspace=ws_name):
                try:
                    model = ws.get_layermodel(r_type, st_name, r_name)
                except ValueError:
                    raise KeyError(r_type)

            if layer.get_mra_metadata("type") != r_type:
                raise webapp.BadRequest("Can't change a \"%s\" layer into a \"%s\"."
                                    % (layer.get_mra_metadata("type"), r_type))
            if wslayer.get_mra_metadata("type") != r_type:
                raise webapp.BadRequest("Can't change a \"%s\" layer into a \"%s\"."
                                    % (wslayer.get_mra_metadata("type"), r_type))

            model.configure_layer(layer, l_enabled)
            model.configure_layer(wslayer, l_enabled)

        # If we have a defaultStyle apply it.
        s_name = data.get("defaultStyle", {}).get("name")
        if s_name:
            with webapp.mightNotFound():
                style = mra.get_style(s_name)

            layer.remove_style(s_name)
            layer.add_style_sld(mf, s_name, style)

            wslayer.remove_style(s_name)
            wslayer.add_style_sld(wsmf, s_name, style)

            # Remove the automatic default style.
            for s_name in layer.iter_styles():
                if s_name == tools.get_dflt_sld_name(layer.ms.type):
                    layer.remove_style(s_name)
            for s_name in wslayer.iter_styles():
                if s_name == tools.get_dflt_sld_name(wslayer.ms.type):
                    wslayer.remove_style(s_name)

        mf.save()
        wsmf.save()

    @HTTPCompatible()
    def DELETE(self, l_name, format):
        """Delete layer <l>."""

        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)

        wsmf = mra.get_service(layer.get_mra_metadata('workspace'))

        with webapp.mightNotFound():
            mf.delete_layer(l_name)
            wsmf.delete_layer(l_name)

        mf.save()
        wsmf.save()


class layerstyles(object):
    """Styles container associated to one layer.

    http://hostname/mra/layers/<l>/styles

    """
    @HTTPCompatible()
    def GET(self, l_name, format):
        """Return all style from layer <l>."""

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


class layerstyle(object):
    """Style associated to layer <l>.

    http://hostname/mra/layers/<l>/styles/<s>

    """
    @HTTPCompatible()
    def DELETE(self, l_name, s_name, format):
        """Remove style <s> from layer <l>."""

        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)
        with webapp.mightNotFound("style", layer=l_name):
            layer.remove_style(s_name)
        mf.save()


class layerfields(object):
    """Attributes (Fields) container associated to layer <l>.

    http://hostname/mra/layers/<l>/fields

    """
    @HTTPCompatible()
    def GET(self, l_name, format):
        mf = mra.get_available()
        with webapp.mightNotFound():
            layer = mf.get_layer(l_name)

        if layer.get_type_name() == "RASTER":
            return {"fields": []}

        fields = [{
            "name": layer.get_metadata("gml_%s_alias" % field, None),
            "type": layer.get_metadata("gml_%s_type" % field, None),
            } for field in layer.iter_fields()]

        geom = layer.get_metadata("gml_geometries", False)
        if geom:
            type = layer.get_metadata("gml_%s_type" % geom, "undefined")
            occurs = layer.get_metadata("gml_%s_occurances" % geom, "0,1").split(",")
            min_occurs, max_occurs = int(occurs[0]), int(occurs[1])
        else:
            geom, type, min_occurs, max_occurs = "undefined", "undefined", 0, 1

        fields.append({
            "name": geom,
            "type": type,
            "minOccurs": min_occurs,
            "maxOccurs": max_occurs,
            })

        return {"fields": fields}


class layergroups(object):
    """Layergroups container.

    http://hostname/mra/layergroups

    """
    @HTTPCompatible()
    def GET(self, format):
        """List all layer groups."""

        mf = mra.get_available()

        return {"layerGroups" : [{
                    "name": lg.name,
                    "href": "%s/layergroups/%s.%s" % (web.ctx.home, lg.name, format)
                    } for lg in mf.iter_layergroups()]
                }

    @HTTPCompatible()
    def POST(self, format):
        """Create a new layer group."""

        mf = mra.get_available()

        data = get_data(name="layerGroup", mandatory=["name"], authorized=["name", "title", "abstract", "layers"])
        lg_name = data.pop("name")
        with webapp.mightNotFound():
            layers = [mf.get_layer(l_name) for l_name in data.pop("layers", [])]

        with webapp.mightConflict():
            lg = mf.create_layergroup(lg_name, data)
        lg.add(*layers)

        mf.save()

        webapp.Created("%s/layergroups/%s.%s" % (web.ctx.home, lg.name, format))


class layergroup(object):
    """A layergroup is a grouping of layers and styles that can be accessed
    as a single layer in a WMS GetMap request.

    http://hostname/mra/layergroups/<lg>

    """
    @HTTPCompatible()
    def GET(self, lg_name, format):
        """Return layergroup <lg>."""

        mf = mra.get_available()
        with webapp.mightNotFound():
            lg = mf.get_layergroup(lg_name)

        latlon_extent = lg.get_latlon_extent()

        bounds = {
            "minx": latlon_extent.minX(),
            "miny": latlon_extent.minY(),
            "maxx": latlon_extent.maxX(),
            "maxy": latlon_extent.maxY(),
            "crs": "EPSG:4326",
            }

        return {"layerGroup": ({
                    "name": lg.name,
                    "mode": "NAMED", # Only available mode in MRA.
                    "publishables": Entries([{
                            "name": layer.ms.name,
                            "href": "%s/layers/%s.%s" % (web.ctx.home, layer.ms.name, format),
                            } for layer in lg.iter_layers()], tag_name="published"),
                    "bounds": Entries(bounds),
                    # TODO: Styles
                    # "styles": [],
                    })
                }

    @HTTPCompatible()
    def PUT(self, lg_name, format):
        """Modify layergroup <lg>."""

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
        """Delete layergroup <lg>."""

        mf = mra.get_available()
        with webapp.mightNotFound():
            mf.delete_layergroup(lg_name)
        mf.save()


class OWSGlobalSettings(object):
    """Control settings of the main OWS service, i.e. the mapfile: layers.map

    http://hostname/mra/services/[wms|wfs|wcs]/settings<lg>

    """
    @HTTPCompatible()
    def GET(self, ows, format):
        """It returns the status of the OGC service."""

        mf = mra.get_available()

        return {
            ows: Entries({
                "enabled": mf.get_metadata("%s_enable_request" % ows) == "*" and True or False,
                "name": ows,
                "schemaBaseURL": mf.get_metadata("ows_schemas_location", "http://schemas.opengis.net"),
                }
            )}

    @HTTPCompatible()
    def PUT(self, ows, format):
        """To enable or disable OGC service..."""

        mf = mra.get_available()
        data = get_data(name=ows, mandatory=["enabled"], authorized=["enabled"])
        is_enabled = data.pop("enabled")
        # TODO: That would be cool to be able to control each operation...
        values = {True: "*", "True": "*", "true": "*",
                  False: "", "False": "", "false": ""}
        if is_enabled not in values:
            raise KeyError("\"%s\" is not valid" % is_enabled)
        mf.set_metadata("%s_enable_request" % ows, values[is_enabled])
        mf.save()


class OWSWorkspaceSettings(object):
    """Control settings of the main OWS service, i.e. the mapfile: layers.map

    http://hostname/mra/services/[wms|wfs|wcs]/settings<lg>

    """
    @HTTPCompatible()
    def GET(self, ws_name, ows, format):
        """It returns the status of the OGC service."""

        mf = mra.get_service(ws_name)

        return {
            ows: Entries({
                "enabled": mf.get_metadata("%s_enable_request" % ows) == "*" and True or False,
                "name": ows,
                "schemaBaseURL": mf.get_metadata("ows_schemas_location", "http://schemas.opengis.net"),
                }
            )}

    @HTTPCompatible()
    def PUT(self, ws_name, ows, format):
        """To enable or disable OGC service..."""

        mf = mra.get_service(ws_name)
        data = get_data(name=ows, mandatory=["enabled"], authorized=["enabled"])
        is_enabled = data.pop("enabled")
        # TODO: That would be cool to be able to control each operation...
        values = {True: "*", "True": "*", "true": "*",
                  False: "", "False": "", "false": ""}
        if is_enabled not in values:
            raise KeyError("\"%s\" is not valid" % is_enabled)
        mf.set_metadata("%s_enable_request" % ows, values[is_enabled])
        mf.save()


# Index:
urlmap(index, "")
# About version:
urlmap(version, "about", "version")
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
# Fonts:
urlmap(fonts, "fonts")
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
urlmap(OWSWorkspaceSettings, "services", "workspaces", (), "(wms|wfs|wcs)", "settings")

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
