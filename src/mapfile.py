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
import re
from xml.etree import ElementTree as etree
import mapscript
import urlparse
import stores
import metadata

import functools

import maptools
from webapp import KeyExists

import tools
from extensions import plugins

class MetadataMixin(object):

    def __getattr__(self, attr):
        if hasattr(self, "ms") and hasattr(metadata, attr):
            return functools.partial(getattr(metadata, attr), self.ms)
        raise AttributeError("'%s' object has no attribute '%s'" %
                             (type(self).__name__, attr))


def get_store_connection_string(info):
    cparam = info["connectionParameters"]
    if cparam.get("dbtype", "") == "postgis":
        return "PG:dbname=%s port=%s host=%s user=%s password=%s" % (
            cparam["database"], cparam["port"], cparam["host"], cparam["user"], cparam["password"])
    elif "url" in cparam:
        url = urlparse.urlparse(cparam["url"])
        if url.scheme != "file" or url.netloc:
            raise ValueError("Only local files are suported.")
        return tools.get_resource_path(url.path)
    else:
        raise ValueError("Unhandled type '%s'" % cparam.get("dbtype", "<unknown>"))


class Class(object):
    """
    """

    def __init__(self, backend):
        self.ms = backend


class Layer(MetadataMixin):
    """
    """

    def __init__(self, backend):
        self.ms = backend

    def enable(self, enabled=True):
        requests = ["GetCapabilities", "GetMap", "GetFeatureInfo", "GetLegendGraphic"]
        self.ms.setMetaData("wms_enable_request",  " ".join(('%s' if enabled else "!%s") % c for c in requests))

    def get_type_name(self):
        return {
            0: "POINT",
            1: "LINESTRING",
            2: "POLYGON",
            3: "RASTER",
            4: "ANNOTATION",
            }[self.ms.type]

    def get_extent(self):
        extent = self.ms.getExtent()
        return stores.Extent(extent.minx, extent.miny, extent.maxx, extent.maxy)

    def get_fields(self):
        fields = self.get_metadata("gml_include_items", "")

        if fields == "all":
            # TODO: Get fields from feature type
            raise NotImplemented()
        elif not fields:
            return []
        else:
            fields = fields.split(",")
        return fields

    def iter_fields(self):
        return iter(self.get_fields())

    def iter_classes(self):
        for i in xrange(self.ms.numclasses):
            yield Class(self.ms.getClass(i))

    def get_styles(self):
        return set(clazz.ms.group for clazz in self.iter_classes())

    def iter_styles(self):
        return iter(self.get_styles())

    def get_SLD(self):
        return self.ms.generateSLD().decode("LATIN1").encode("UTF8")

    def add_style_sld(self, mf, s_name, new_sld):

        # Because we do not want to apply the sld to real layers by mistake
        # we need to rename it to something we are sure is not used.
        sld_layer_name = "__mra_tmp_template"

        # This is realy ugly but etree has trouble with namespaces...
        # TODO: Do this again in an other way.
        fixedxml = re.sub(' [a-zzA-Z0-9]+:([a-zA-Z0-9]+=")', ' \\1', new_sld)
        xmlsld = etree.fromstring(fixedxml)

        # Still problems with namespaces...
        for child in xmlsld.getchildren():
            if child.tag.endswith("NamedLayer"):
                for gchild in child.getchildren():
                    if gchild.tag.endswith("Name"):
                        gchild.text = sld_layer_name
                        break
                else:
                    continue
            break
        else:
            raise ValueError("Bad sld (No NamedLayer/Name)")


        etree.register_namespace("", "http://www.opengis.net/sld")
        new_sld = etree.tostring(xmlsld)

        ms_template_layer = self.ms.clone()
        ms_template_layer.name = sld_layer_name
        mf.ms.insertLayer(ms_template_layer)

        ms_template_layer.applySLD(new_sld, sld_layer_name)
        for i in xrange(ms_template_layer.numclasses):
            ms_class = ms_template_layer.getClass(i)
            ms_class.group = s_name
            self.ms.insertClass(ms_class)

        mf.ms.removeLayer(ms_template_layer.index)

    def remove_style(self, s_name):
        for c_index in reversed(xrange(self.ms.numclasses)):
            c = self.ms.getClass(c_index)
            if c.group == s_name:
                self.ms.removeClass(c_index)
                break
        else:
            raise KeyError(s_name)

    def update(self, metadata):
        self.update_metadatas(metadata)


class LayerGroup(object):
    """
    """

    # TODO: We need to handle the order of the layers in a group.

    def __init__(self, name, mapfile):
        """
        """

        self.name = name
        self.mapfile = mapfile

    def iter_layers(self):
        return self.mapfile.iter_layers(meta={"wms_group_name":self.name})

    def get_layers(self):
        return list(self.iter_layers())

    def add_layer(self, layer):
        layer.ms.group = self.name
        layer.set_metadata("wms_group_name", self.name)
        for k, v in self.mapfile.get_mra_metadata("layergroups")[self.name]:
            layer.set_metadata("wms_group_%s" % k, v)

    def add(self, *args):
        for layer in args:
            if isinstance(layer, basestring):
                layer = self.mapfile.get_layer(layer)
            self.add_layer(layer)

    def remove_layer(self, layer):
        layer.ms.group = None
        for mkey in layer.get_metadata_keys():
            # (We really do not want to use iter_metadata_keys())
            if mkey.startswith("wms_group_"):
                layer.del_metadata(mkey)

    def remove(self, *args):
        for layer in args:
            if isinstance(layer, basestring):
                layer = mapfile.get_layer(layer)
            self.remove_layer(layer)

    def clear(self):
        # Remove all the layers from this group.
        for layer in self.mapfile.iter_layers(attr={"group": self.name}):
            self.remove_layer(layer)

    def get_extent(self):
        layers = self.get_layers()
        if not layers:
            return stores.Extent(0, 0, 0, 0)

        extent = layers[0].get_extent()
        for layer in layers[1:]:
            e = layer.get_extent()
            extent.addX(e.minX(), e.maxX())
            extent.addY(e.minY(), e.maxY())

        return extent

class LayerModel(MetadataMixin):
    """
    """

    def __init__(self, backend):
        self.ms = backend
        self.name = self.get_mra_metadata("name", None)

    def get_extent(self):
        extent = self.ms.getExtent()
        return stores.Extent(extent.minx, extent.miny, extent.maxx, extent.maxy)

    def get_latlon_extent(self):
        rect = mapscript.rectObj(*self.get_extent())
        res = rect.project(mapscript.projectionObj(self.ms.getProjection()),
                           mapscript.projectionObj('+init=epsg:4326'))
        return stores.Extent(rect.minx, rect.miny, rect.maxx, rect.maxy)

    def get_proj4(self):
        return self.ms.getProjection()

    def get_wkt(self):
        return tools.proj4_to_wkt(self.ms.getProjection())

    def get_authority(self):
        return tools.wkt_to_authority(self.get_wkt())


class FeatureTypeModel(LayerModel):
    """
    """

    def update(self, ws, ft_name, ds_name, metadata):

        ds = ws.get_datastore(ds_name)
        ft = ds[ft_name]
        self.name = ft_name

        # Set basic attributes.
        self.ms.name = "ft:%s:%s:%s" % (ws.name, ds_name, ft_name)
        self.ms.status = mapscript.MS_OFF
        self.ms.type = ft.get_geomtype_mapscript()
        self.ms.setProjection(ft.get_proj4())
        self.ms.setExtent(*ft.get_extent())

        # Configure the connection to the store.
        # This is a little hacky as we have to translate stuff...
        info = ws.get_datastore_info(ds_name)
        cparam = info["connectionParameters"]
        if cparam.get("dbtype", None) in ["postgis", "postgres", "postgresql"]:
            self.ms.connectiontype = mapscript.MS_POSTGIS
            self.ms.connection = "dbname=%s port=%s host=%s user=%s password=%s" % (
                cparam["database"], cparam["port"], cparam["host"], cparam["user"], cparam["password"])
            self.ms.data = "%s FROM %s" % (ds[ft_name].get_geometry_column(), ft_name)
            self.set_metadata("ows_extent", "%s %s %s %s" %
                (ft.get_extent().minX(), ft.get_extent().minY(),
                ft.get_extent().maxX(), ft.get_extent().maxY())
                )
        #elif cpram["dbtype"] in ["shp", "shapefile"]:
        else:
            self.ms.connectiontype = mapscript.MS_SHAPEFILE
            url = urlparse.urlparse(cparam["url"])
            self.ms.data = tools.get_resource_path(url.path)

            # TODO: strip extention.
        #else:
        #    raise ValueError("Unhandled type '%s'" % info["dbtype"])

        # Deactivate wms and wfs requests, because we are a virtual layer.
        self.set_metadata("wms_enable_request", "!GetCapabilities !GetMap !GetFeatureInfo !GetLegendGraphic")
        self.set_metadata("wfs_enable_request", "!GetCapabilities !DescribeFeatureType !GetFeature")

        # Update mra metadatas, and make sure the mandatory ones are left untouched.
        self.update_mra_metadatas(metadata)
        self.update_mra_metadatas({"name": ft_name, "type": "featuretype", "storage": ds_name,
                                   "workspace": ws.name, "is_model": True})

    def configure_layer(self, ws, layer, enabled=True):

        plugins.extend("pre_configure_feature", self, ws, layer)

        # We must also update all our personal attributes (type, ...)
        # because we might not have been cloned.

        layer.ms.type = self.ms.type
        layer.ms.setProjection(self.ms.getProjection())
        layer.ms.setExtent(self.ms.extent.minx, self.ms.extent.miny,
                           self.ms.extent.maxx, self.ms.extent.maxy)
        layer.ms.data = self.ms.data
        layer.ms.connectiontype = self.ms.connectiontype
        layer.ms.connection = self.ms.connection

        layer.update_mra_metadatas({
                "name": self.get_mra_metadata("name"),
                "type": self.get_mra_metadata("type"),
                "storage": self.get_mra_metadata("storage"),
                "workspace": self.get_mra_metadata("workspace"),
                "is_model": False,
                })

        layer.update_metadatas({
                "wfs_name": layer.get_metadata("wms_name"),
                "wfs_title": layer.get_metadata("wms_title"),
                "wfs_abstract": layer.get_metadata("wms_abstract"),
                })

        if enabled:
            layer.ms.setMetaData("wfs_enable_request", "GetCapabilities GetFeature DescribeFeatureType")

        layer.set_metadata("wfs_srs", "EPSG:4326")
        layer.ms.setMetaData("wfs_getfeature_formatlist", "OGRGML,SHAPEZIP")
        layer.ms.setMetaData("gml_types", "auto")

        # TODO: layer.ms.setMetaData("wfs_metadataurl_format", "")
        # TODO: layer.ms.setMetaData("wfs_metadataurl_href", "")
        # TODO: layer.ms.setMetaData("wfs_metadataurl_type", "")
        # TODO: layer.ms.setMetaData("gml_xml_items", "")

        # Configure the layer based on information from the store.
        ds = ws.get_datastore(self.get_mra_metadata("storage"))
        ft = ds[self.get_mra_metadata("name")]

        # Configure the different fields.
        field_names = []
        for field in ft.iterfields():
            layer.set_metadata("gml_%s_alias" % field.get_name(), field.get_name())
            layer.set_metadata("gml_%s_type" % field.get_name(), field.get_type_gml())
            #TODO: layer.set_metadata("gml_%s_precision" field.get_name(), "")
            #TODO: layer.set_metadata("gml_%s_width" field.get_name(), "")
            #TODO: layer.set_metadata("gml_%s_value" field.get_name(), "")
            field_names.append(field.get_name())
        layer.set_metadata("wfs_include_items", ",".join(field_names))
        layer.set_metadata("gml_include_items", ",".join(field_names))

        # TODO: layer.set_metadata("wfs_featureid", "")
        # TODO: layer.set_metadata("gml_featureid", "")
        layer.set_metadata("gml_geometries", ft.get_geometry_column())
        layer.set_metadata("gml_%s_type" % ft.get_geometry_column(), ft.get_geomtype_gml())
        # TODO: layer.set_metadata("gml_%s_occurances" ft.get_geometry_column(), "")

        # TODO: Check if class already exists.
        # If no class exists we add a new class by default
        if layer.ms.type == mapscript.MS_LAYER_POINT:
            maptools.create_def_point_class(layer.ms)
        elif layer.ms.type == mapscript.MS_LAYER_LINE:
            maptools.create_def_line_class(layer.ms)
        elif layer.ms.type == mapscript.MS_LAYER_POLYGON:
            maptools.create_def_polygon_class(layer.ms)



class CoverageModel(LayerModel):
    """
    """

    def update(self, ws, c_name, cs_name, metadata):

        cs = ws.get_coveragestore(cs_name)
        self.name = c_name

        # Set basic attributes.
        self.ms.name = "c:%s:%s" % (cs_name, c_name)
        self.ms.status = mapscript.MS_OFF
        self.ms.type = mapscript.MS_LAYER_RASTER
        self.ms.setProjection(cs.get_proj4())
        self.ms.setExtent(*cs.get_extent())
        self.ms.setProcessingKey("RESAMPLE","AVERAGE")

        # Configure the connection to the store.
        # This is a little hacky as we have to translate stuff...
        info = ws.get_coveragestore_info(cs_name)
        cparam = info["connectionParameters"]

        #if cparam["dbtype"] in ["tif", "tiff"]:
        self.ms.connectiontype = mapscript.MS_RASTER
        url = urlparse.urlparse(cparam["url"])
        self.ms.data = tools.get_resource_path(url.path)
            # TODO: strip extention.
        #else:
        #    raise ValueError("Unhandled type '%s'" % cparam["dbtype"])

        # Deactivate wms and wcs requests, because we are a virtual layer.
        self.set_metadata("wms_enable_request", "!GetCapabilities !GetMap !GetFeatureInfo !GetLegendGraphic")
        self.set_metadata("wcs_enable_request", "!GetCapabilities !DescribeCoverage !GetCoverage")

        # Update mra metadatas, and make sure the mandatory ones are left untouched.
        self.update_mra_metadatas(metadata)
        self.update_mra_metadatas({"name": c_name, "type": "coverage", "storage": cs_name,
                                   "workspace": ws.name, "is_model": True})

    def configure_layer(self, ws, layer, enabled=True):

        plugins.extend("pre_configure_coverage", self, ws, layer)

        # We must also update all our personal attributes (type, ...)
        # because we might not have been cloned.

        layer.ms.type = self.ms.type
        layer.ms.setProjection(self.ms.getProjection())
        layer.ms.setExtent(self.ms.extent.minx, self.ms.extent.miny,
                           self.ms.extent.maxx, self.ms.extent.maxy)
        layer.ms.setProcessingKey("RESAMPLE","AVERAGE")
        layer.ms.data = self.ms.data
        layer.ms.connectiontype = self.ms.connectiontype
        layer.ms.connection = self.ms.connection

        layer.update_mra_metadatas({
                "name": self.get_mra_metadata("name"),
                "type": self.get_mra_metadata("type"),
                "storage": self.get_mra_metadata("storage"),
                "workspace": self.get_mra_metadata("workspace"),
                "is_model": False,
                })

        layer.set_metadatas({
                "wfs_name": layer.get_metadata("wms_name"),
                "wfs_title": layer.get_metadata("wms_title"),
                "wfs_abstract": layer.get_metadata("wms_abstract"),
                #"wfs_keywordlist": layer.get_metadata("wms_keywordlist"),
                })

        if enabled:
            layer.ms.setMetaData("wcs_enable_request", "GetCapabilities GetCoverage DescribeCoverage")

        # TODO: layer.set_metadata("wcs_srs", "")
        # TODO: layer.set_metadata("wcs_getfeature_formatlist", "")
        # TODO: layer.set_metadata("wcs_metadataurl_format", "")
        # TODO: layer.set_metadata("wcs_metadataurl_href", "")
        # TODO: layer.set_metadata("wcs_metadataurl_type", "")
        # ...


class Workspace(object):
    pass

class MapfileWorkspace(Workspace):
    """ A workspace representing a whole mapfile.
    This is currently the only existing type of workspace,
    but there should be others that can handle subsets of
    the mapfile.
    """

    def __init__(self, mapfile):
        # We are obvliously the default workspace.
        self.name = mapfile.get_default_workspace_name()
        self.mapfile = mapfile

    def save(self):
        """Saves the workspace to disk, same as calling save on the
        associated mapfile.
        """
        self.mapfile.save()

    # Stores:
    def get_store(self, st_type, name):
        st_type = st_type if st_type.endswith("s") else st_type + "s"
        cparam = get_store_connection_string(self.get_store_info(st_type, name))
        if st_type == "datastores":
            return stores.Datastore(cparam)
        elif st_type == "coveragestores":
            return stores.Coveragestore(cparam)

    def get_store_info(self, st_type, name):
        st_type = st_type if st_type.endswith("s") else st_type + "s"
        info = self.mapfile.get_mra_metadata(st_type, {})[name].copy()
        info["name"] = name
        return info

    def iter_store_names(self, st_type):
        st_type = st_type if st_type.endswith("s") else st_type + "s"
        return self.mapfile.get_mra_metadata(st_type, {}).iterkeys()

    def iter_stores(self, st_type):
        st_type = st_type if st_type.endswith("s") else st_type + "s"
        return self.mapfile.get_mra_metadata(st_type, {}).iteritems()

    def create_store(self, st_type, name, configuration):
        st_type = st_type if st_type.endswith("s") else st_type + "s"
        with self.mapfile.mra_metadata(st_type, {}) as stores:
            if name in stores:
                raise KeyExists(name)
            stores[name] = configuration

    def update_store(self, st_type, name, configuration):
        st_type = st_type if st_type.endswith("s") else st_type + "s"
        with self.mapfile.mra_metadata(st_type, {}) as stores:
            stores[name].update(configuration)

    def delete_store(self, st_type, name):
        st_type = st_type if st_type.endswith("s") else st_type + "s"
        with self.mapfile.mra_metadata(st_type, {}) as stores:
            del stores[name]


    # Datastores:

    def get_datastore(self, name):
        """Returns a store.Datastore object from the workspace."""
        return self.get_store("datastores", name)

    def get_datastore_info(self, name):
        """Returns info for a datastore from the workspace."""
        return self.get_store_info("datastores", name)

    def iter_datastore_names(self):
        """Return an iterator over the datastore names."""
        return self.iter_store_names("datastores")

    def iter_datastores(self):
        """Return an iterator over the datastore (names, configuration)."""
        return self.iter_stores("datastores")

    def create_datastore(self, name, configuration):
        """Creates a new datastore."""
        return self.create_store("datastores", name, configuration)

    def update_datastore(self, name, configuration):
        """Update a datastore."""
        return self.update_store("datastores", name, configuration)

    def delete_datastore(self, name):
        """Delete a datastore."""
        return self.delete_store("datastores", name)

    # Coveragestores (this is c/p from datastores):

    def get_coveragestore(self, name):
        """Returns a store.Coveragestore object from the workspace."""
        return self.get_store("coveragestores", name)

    def get_coveragestore_info(self, name):
        """Returns info for a coveragestore from the workspace."""
        return self.get_store_info("coveragestores", name)

    def iter_coveragestore_names(self):
        """Return an iterator over the coveragestore names."""
        return self.iter_store_names("coveragestores")

    def iter_coveragestores(self):
        """Return an iterator over the coveragestore (names, configuration)."""
        return self.iter_stores("coveragestores")

    def create_coveragestore(self, name, configuration):
        """Creates a new coveragestore."""
        return self.create_store("coveragestores", name, configuration)

    def update_coveragestore(self, name, configuration):
        """Update a coveragestore."""
        return self.update_store("coveragestores", name, configuration)

    def delete_coveragestore(self, name):
        """Delete a coveragestore."""
        return self.delete_store("coveragestores", name)

    # Feature types

    def iter_featuretypemodels(self, ds_name=None, **kwargs):
        kwargs.setdefault("mra", {}).update({"type":"featuretype", "is_model":True})
        if ds_name != None:
            kwargs["mra"].update({"storage":ds_name, "workspace":self.name})
        for ms_layer in self.mapfile.iter_ms_layers(**kwargs):
            yield FeatureTypeModel(ms_layer)

    def get_featuretypemodel(self, ft_name, ds_name):
        # Improvement: Use get by name combined with a coverage-specific naming.
        try:
            return next(self.iter_featuretypemodels(ds_name, mra={"name":ft_name}))
        except StopIteration:
            raise KeyError((ds_name, ft_name))

    def has_featuretypemodel(self, ft_name, ds_name):
        # Improvement: See get_featuretypemodel
        try:
            self.get_featuretypemodel(ft_name, ds_name)
        except KeyError:
            return False
        else:
            return True

    def create_featuretypemodel(self, ft_name, ds_name, metadata={}):
        if self.has_featuretypemodel(ft_name, ds_name):
            raise KeyExists(ft_name)

        ft = FeatureTypeModel(mapscript.layerObj(self.mapfile.ms))
        ft.update(self, ft_name, ds_name, metadata)
        return ft

    def update_featuretypemodel(self, ft_name, ds_name, metadata={}):
        ft = self.get_featuretypemodel(ft_name, ds_name)
        ft.update(self, ft_name, ds_name, metadata)

    def delete_featuretypemodel(self, ft_name, ds_name):
        try:
            next(self.mapfile.iter_layers(mra={"workspace":self.name, "type":"featuretype",
                                               "storage":ds_name, "name":ft_name}))
        except StopIteration:
            pass # No layers use our featuretyp, all OK.
        else:
            raise ValueError("The featuretype '%s' can't be delete because it is used." % ft_name)

        ft = self.get_featuretypemodel(ft_name, ds_name)
        self.mapfile.ms.removeLayer(ft.ms.index)


    # Coverages

    def iter_coveragemodels(self, cs_name=None, **kwargs):
        kwargs.setdefault("mra", {}).update({"type":"coverage", "is_model":True})
        if cs_name != None:
            kwargs["mra"].update({"storage":cs_name, "workspace":self.name})
        for ms_layer in self.mapfile.iter_ms_layers(**kwargs):
            yield CoverageModel(ms_layer)

    def get_coveragemodel(self, c_name, cs_name):
        # Improvement: Use get by name combined with a coverage-specific naming.
        try:
            return next(self.iter_coveragemodels(cs_name, mra={"name":c_name}))
        except StopIteration:
            raise KeyError((cs_name, c_name))

    def has_coveragemodel(self, c_name, cs_name):
        # Improvement: See get_coveragemodel
        try:
            self.get_coveragemodel(c_name, cs_name)
        except KeyError:
            return False
        else:
            return True

    def create_coveragemodel(self, c_name, cs_name, metadata={}):
        if self.has_coveragemodel(c_name, cs_name):
            raise KeyExists(c_name)

        c = CoverageModel(mapscript.layerObj(self.mapfile.ms))
        c.update(self, c_name, cs_name, metadata)
        return c

    def update_coveragemodel(self, c_name, cs_name, metadata={}):
        c = self.get_coveragemodel(c_name, cs_name)
        c.update(self, c_name, cs_name, metadata)

    def delete_coveragemodel(self, c_name, cs_name):
        try:
            next(self.mapfile.iter_layers(mra={"workspace":self.name, "type":"coverage",
                                               "storage":cs_name, "name":c_name}))
        except StopIteration:
            pass # No layers use our featuretyp, all OK.
        else:
            raise ValueError("The coverage '%s' can't be delete because it is used." % c_name)

        c = self.get_coveragemodel(c_name, cs_name)
        self.mapfile.ms.removeLayer(c.ms.index)

    # All the above :)

    def get_model(self, m_name, s_type, s_name):

        if s_type == "coverage":
            return self.get_coveragemodel(m_name, s_name)
        elif s_type == "featuretype":
            return self.get_featuretypemodel(m_name, s_name)
        else:
            raise ValueError("Bad storage type '%s'." % s_type)


class Mapfile(MetadataMixin):
    """
    """

    def __init__(self, path, root=None):

        if root != None:
            full_path = os.path.realpath(os.path.join(root, "%s.map" % path))
            if not full_path.startswith(root):
                raise IOError("mapfile '%s' outside root directory." % (path))
            path = full_path
        if isinstance(path, mapscript.mapObj):
            self.path = None
            self.ms = path
        else:
            self.path = path
            self.ms = mapscript.mapObj(self.path)

        self.filename = os.path.basename(self.path)

        # We have one workspace that represents the file.
        self.__default_workspace = MapfileWorkspace(self)

    def save(self, path=None):
        if path is None:
            path = self.path
        self.ms.save(path)

    def rawtext(self):
        open(self.path, "r").read()

    def update(self, configuration):
        raise NotImplemented()

    # Layers:

    def iter_ms_layers(self, attr={}, meta={}, mra={}):
        def check(f, v):
            return f(v) if callable(f) else f == v

        for l in xrange(self.ms.numlayers):
            ms_layer = self.ms.getLayer(l)
            if not all(check(checker, getattr(ms_layer, k, None)) for k, checker in attr.iteritems()):
                continue
            if not all(check(checker, metadata.get_metadata(ms_layer, k, None)) for k, checker in meta.iteritems()):
                continue
            if not all(check(checker, metadata.get_mra_metadata(ms_layer, k, None)) for k, checker in mra.iteritems()):
                continue
            yield ms_layer

    def iter_layers(self, **kwargs):
        kwargs.setdefault("mra", {}).update({"is_model": lambda x: x != True})
        for ms_layer in self.iter_ms_layers(**kwargs):
            yield Layer(ms_layer)

    def get_layer(self, l_name):
        try:
            return next(self.iter_layers(attr={"name": l_name}))
        except StopIteration:
            raise KeyError(l_name)

    def has_layer(self, l_name):
        try:
            self.get_layer(l_name)
        except KeyError:
            return False
        else:
            return True

    def get_layer_wsm(self, l_name):
        layer = self.get_layer(l_name)
        ws = self.get_workspace(layer.get_mra_metadata("workspace"))
        model = ws.get_model(m_name=layer.get_mra_metadata("name"),
                             s_type=layer.get_mra_metadata("type"),
                             s_name=layer.get_mra_metadata("storage"))
        return layer, ws, model

    def create_layer(self, ws, model, l_name, l_enabled, l_metadata={}):
        # First create the layer, then configure it.

        if self.has_layer(l_name):
            raise KeyExists(l_name)

        # We still clone, because we have to start from something,
        # but everything should be configured() anyway.
        layer = Layer(model.ms.clone())
        layer.ms.name = l_name
        layer.ms.status = mapscript.MS_ON
        layer.ms.dump = mapscript.MS_TRUE
        layer.ms.tolerance = 6
        layer.ms.toleranceunits = mapscript.MS_PIXELS
        layer.ms.template = "foo.html"

        layer.enable(l_enabled)
        self.ms.insertLayer(layer.ms)

        l_metadata["wms_name"] = l_name
        l_metadata.setdefault("wms_title", l_name)
        l_metadata.setdefault("wms_abstract", l_name)
        l_metadata.setdefault("wms_bbox_extended", "true")

        # TODO: Add other default values as above:
        # "wms_keywordlist"
        # "wms_keywordlist_vocabulary"
        # "wms_keywordlist_<vocabulary>_items"
        # "wms_srs"
        # "wms_dataurl_format"
        # "wms_dataurl_href"
        # "wms_getmap_formatlist"
        # "wms_getfeatureinfo_formatlist"
        # "wms_getlegendgraphic_formatlist"
        # "wms_attribution_title"
        # "wms_attribution_onlineresource": ""
        # "wms_attribution_logourl_href"
        # "wms_attribution_logourl_format"
        # "wms_attribution_logourl_height"
        # "wms_attribution_logourl_width"
        # "wms_identifier_authority"
        # "wms_identifier_value"
        # "wms_authorityurl_name"
        # "wms_authorityurl_href"
        # "wms_metadataurl_type"
        # "wms_metadataurl_href"
        # "wms_metadataurl_format"

        # TODO: pass correct data (title, abstract, ...) to layer.update()
        layer.update(l_metadata)
        model.configure_layer(ws, layer, l_enabled)

        return layer

    def delete_layer(self, l_name):
        layer = self.get_layer(l_name)
        self.ms.removeLayer(layer.ms.index)

    # Layergroups

    def create_layergroup(self, lg_name, mra_metadata={}):
        with self.mra_metadata("layergroups", {}) as layergroups:
            if lg_name in layergroups:
                raise KeyExists(lg_name)
            layergroups[lg_name] = mra_metadata
        return LayerGroup(lg_name, self)

    def iter_layergroups(self):
        return (LayerGroup(name, self) for name in self.get_mra_metadata("layergroups", {}).iterkeys())

    def get_layergroup(self, lg_name):
        if lg_name in self.get_mra_metadata("layergroups", {}):
            return LayerGroup(lg_name, self)
        else:
            raise KeyError(lg_name)

    def add_to_layergroup(self, lg_name, *args):
        lg = self.get_layergroup(lg_name)
        lg.add(*args)

    def remove_from_layergroup(self, lg_name, *args):
        lg = self.get_layergroup(lg_name)
        lg.remove(*args)

    def delete_layergroup(self, lg_name):

        layer_group = self.get_layergroup(lg_name)
        # Remove all the layers from this group.
        for layer in self.iter_layers(attr={"group": layer_group.name}):
            layer_group.remove(layer)

        # Remove the group from mra metadats.
        with self.mra_metadata("layergroups", {}) as layergroups:
            del layergroups[lg_name]


    # Styles:

    def iter_styles(self):
        return iter(self.get_styles())

    def get_styles(self):
        # The group name is the style"s name.

        styles = set()
        for layer in self.iter_layers():
            for clazz in layer.iter_classes():
                styles.add(clazz.ms.group)

        return styles

    def get_style_sld(self, s_name):
        # Because styles do not really exist here, we first need to find
        # a layer that has the style we want.

        for layer in self.iter_layers():
            if s_name in layer.get_styles():
                break
        else:
            raise KeyError(s_name)

        # This is a ugly hack. We clone the layer and remove all the other styles.
        # Then we ask mapscript to generate the sld, but aprently for that the
        # cloned style needs to be in the mapfile... so be it.

        clone = layer.ms.clone()
        for c_index in reversed(xrange(clone.numclasses)):
            c = clone.getClass(c_index)
            if c.group != s_name:
                clone.removeClass(c_index)

        self.ms.insertLayer(clone)
        sld = Layer(clone).get_SLD()
        self.ms.removeLayer(clone.index)

        return sld

    # Workspaces:

    def get_default_workspace_name(self):
        return self.get_mra_metadata("default_workspace", "default")

    def set_default_workspace_name(self, name):
        self.set_mra_metadata("default_workspace", name)

    def iter_workspaces(self):
        """iter_ates over the workspaces managed by a mapfile.
        For current version, only "default" workspace is available which
        correspond to the current mapfile. The relationship between default
        workspace and mapfile is one to one.
        However there is currently work underway to change this...
        """
        yield self.get_default_workspace()

    def get_workspaces(self):
        """Gets workspaces from mapfile that match all the specified conditions.
        For the moment this is equivalent to iter_workspaces, because workpspaces
        are still a "virtual" notion and do not really exist.
        """
        return list(self.iter_workspaces())

    def get_workspace(self, name):
        if name != self.get_default_workspace_name():
            raise KeyError(name)
        return self.get_default_workspace()

    def get_default_workspace(self):
        return self.__default_workspace

    # Let"s delegate other stuff to the default workspace.
    # def __getattr__(self, name):
    #     if hasattr(self, "__default_workspace"):
    #         return getattr(self.__default_workspace, name)
