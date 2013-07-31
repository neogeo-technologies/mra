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
import os.path

import functools
import yaml

import mapscript

from webapp import KeyExists

import metadata

class MetadataMixin(object):

    def __getattr__(self, attr):
        if hasattr(self, "ms") and hasattr(metadata, attr):
            return functools.partial(getattr(metadata, attr), self.ms)
        raise AttributeError("'%s' object has no attribute '%s'" %
                             (type(self).__name__, attr))

class Layer(MetadataMixin):
    def __init__(self, backend):
        self.ms = backend

    def update(self, name, enabled, metadata):
        self.ms.name = name
        self.ms.template = "foo.html" # TODO: Support html format response

        self.enable(enabled)
        self.update_metadatas(metadata)

    def enable(self, enabled=True):
        requests = ["GetCapabilities", "GetMap", "GetFeatureInfo", "GetLegendGraphic"]
        self.ms.status = mapscript.MS_ON if enabled else mapscript.MS_OFF
        self.set_metadata("wms_enable_request", " ".join(('%s' if enabled else "!%s") % c for c in requests))

    def get_type_name(self):
        return {
            0: "POINT",
            1: "LINESTRING",
            2: "POLYGON",
            3: "RASTER",
            4: "ANNOTATION",
            }[self.ms.type]

    def get_proj4(self):
        return self.ms.getProjection()

    def get_wkt(self):
        return tools.proj4_to_wkt(self.ms.getProjection())

    def get_authority(self):
        return tools.wkt_to_authority(self.get_wkt())

    def get_authority_name(self):
        return self.get_authority()[0]

    def get_authority_code(self):
        return self.get_authority()[1]

    def get_extent(self):
        extent = self.ms.getExtent()
        return stores.Extent(extent.minx, extent.miny, extent.maxx, extent.maxy)

    def get_latlon_extent(self):
        rect = mapscript.rectObj(*self.get_extent())
        res = rect.project(mapscript.projectionObj(self.get_proj4()),
                           mapscript.projectionObj('+init=epsg:4326'))
        return stores.Extent(rect.minx, rect.miny, rect.maxx, rect.maxy)

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

        # Most xml parsers will have trouble with the kind of mess we get as sld.
        # Mostly because we haven't got the proper declarations, we fallback to
        # an html parser, which luckily is much more forgiving.
        from xml.dom.minidom import parseString
        xmlsld = parseString(new_sld)

        try:
            xmlsld.firstChild.getElementsByTagName("NamedLayer")[0]\
                .getElementsByTagName("Name")[0].firstChild.data = sld_layer_name
        except:
            raise ValueError("Bad sld (No NamedLayer/Name)")

        # Remove encoding ?
        # @wapiflapi Mapscript ne gère pas les espaces...
        new_sld = xmlsld.toxml()

        ms_template_layer = self.ms.clone()
        ms_template_layer.name = sld_layer_name
        mf.ms.insertLayer(ms_template_layer)

        try:
            ms_template_layer.applySLD(new_sld, sld_layer_name)
        except:
            raise ValueError("Unable to access storage.")

        for i in xrange(ms_template_layer.numclasses):
            ms_class = ms_template_layer.getClass(i)
            ms_class.group = s_name
            self.ms.insertClass(ms_class)

        mf.ms.removeLayer(ms_template_layer.index)

    def set_default_style(self, mf):

        if self.ms.type == mapscript.MS_LAYER_POINT:
            self.ms.tolerance = 8
            self.ms.toleranceunits = 6
            s_name = 'default_point'
        elif self.ms.type == mapscript.MS_LAYER_LINE:
            self.ms.tolerance = 8
            self.ms.toleranceunits = 6
            s_name = 'default_line'
        elif self.ms.type == mapscript.MS_LAYER_POLYGON:
            self.ms.tolerance = 0
            self.ms.toleranceunits = 6
            s_name = 'default_polygon'
        else:
            return

        try:
            style = open(os.path.join(os.path.dirname(__file__), "%s.sld" % s_name)).read()
        except IOError, OSError:
            return

        self.add_style_sld(mf, s_name, style)
        self.ms.classgroup = s_name

    def remove_style(self, s_name):
        for c_index in reversed(xrange(self.ms.numclasses)):
            c = self.ms.getClass(c_index)
            if c.group == s_name:
                self.ms.removeClass(c_index)
                break
        else:
            raise KeyError(s_name)


class Layergroup(object):

    def __init__(self, name, mapfile):
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
        self.mapfile.move_layer_down(layer.ms.name)

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

    def get_latlon_extent(self):
        layers = self.get_layers()
        if not layers:
            return stores.Extent(0, 0, 0, 0)

        extent = layers[0].get_latlon_extent()
        for layer in layers[1:]:
            e = layer.get_latlon_extent()
            extent.addX(e.minX(), e.maxX())
            extent.addY(e.minY(), e.maxY())

        return extent


class Mapfile(MetadataMixin):

    def __init__(self, path, create=False):
        self.path = path
        self.filename = os.path.basename(self.path)
        self.name = os.path.splitext(self.filename)[0]

        if create and os.path.exists(self.path):
            raise KeyExists(self.filename)

        if create:
            self.ms = mapscript.mapObj()
        else:
            self.ms = mapscript.mapObj(self.path)

    def save(self, path=None):
        self.ms.save(path or self.path)

    def rawtext(self):
        open(self.path, "r").read()


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

    def create_layer(self, model, l_name, l_enabled, l_metadata={}):
        if self.has_layer(l_name):
            raise KeyExists(l_name)

        # Create the layer.
        layer = Layer(mapscript.layerObj(self.ms))

        dflt_metadata = {
            "wms_title": l_name,
            "wms_abstract": l_name,
            "wms_bbox_extended": "true",
            # TODO: Add other default values as above:
            # wms_keywordlist, wms_keywordlist_vocabulary, wms_keywordlist_<vocabulary>_items
            # wms_srs, wms_dataurl_(format|href), ows_attribution_(title|onlineresource)
            # ows_attribution_logourl_(href|format|height|width), ows_identifier_(authority|value)
            # ows_authorityurl_(name|href), ows_metadataurl_(type|href|format)
            }
        for k, v in dflt_metadata.iteritems():
            l_metadata.setdefault(k, v)
        l_metadata["wms_name"] = l_name

        # Update layer.
        layer.update(l_name, l_enabled, l_metadata)

        # Configure the layer according to the model.
        model.configure_layer(layer, l_enabled)

        # Set default style.
        layer.set_default_style(self)

    def delete_layer(self, l_name):
        layer = self.get_layer(l_name)
        self.ms.removeLayer(layer.ms.index)

    def move_layer_up(self, l_name):
        layer = self.get_layer(l_name)
        self.ms.moveLayerUp(layer.ms.index)

    def move_layer_down(self, l_name):
        layer = self.get_layer(l_name)
        self.ms.moveLayerDown(layer.ms.index)


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
        layer_group.clear()
        # Remove the group from mra metadata.
        with self.mra_metadata("layergroups", {}) as layergroups:
            del layergroups[lg_name]




# Workspaces are special Mapfiles that are composed of LayerModels
# which are layers that can be used to configure other layers.


class LayerModel(Layer):
    def __init__(self, ws, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self.ws = ws
        self.name = self.get_mra_metadata("name", None)

class FeatureTypeModel(LayerModel):

    def update(self, ds_name, ft_name, metadata):
        ws = self.ws

        # Make sure the datastore exists.
        ds = ws.get_datastore(ds_name)

        ft = ds[ft_name]
        self.name = ft_name

        # Set basic attributes.
        self.ms.name = "ft:%s:%s" % (ds_name, ft_name)
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
            connection = "dbname=%s port=%s host=%s " % (cparam["database"], cparam["port"], cparam["host"])
            connection += " ".join("%s=%s" % (p, cparam[p]) for p in ["user", "password"] if p in cparam)
            self.ms.connection = connection
            self.ms.data = "%s FROM %s" % (ds[ft_name].get_geometry_column(), ft_name)
            self.set_metadata("ows_extent", "%s %s %s %s" %
                (ft.get_extent().minX(), ft.get_extent().minY(),
                ft.get_extent().maxX(), ft.get_extent().maxY()))
        #elif cpram["dbtype"] in ["shp", "shapefile"]:
        # TODO: clean up this fallback.
        else:
            self.ms.connectiontype = mapscript.MS_SHAPEFILE
            url = urlparse.urlparse(cparam["url"])
            self.ms.data = tools.get_resource_path(url.path)

        # Deactivate wms and wfs requests, because we are a virtual layer.
        self.set_metadatas({
            "wms_enable_request": "!GetCapabilities !GetMap !GetFeatureInfo !GetLegendGraphic",
            "wfs_enable_request": "!GetCapabilities !DescribeFeatureType !GetFeature",
            })

        # Update mra metadatas, and make sure the mandatory ones are left untouched.
        self.update_mra_metadatas(metadata)
        self.update_mra_metadatas({"name": ft_name, "type": "featuretype", "storage": ds_name})


    def configure_layer(self, layer, enabled=True):
        ws = self.ws

        plugins.extend("pre_configure_vector_layer", self, ws, layer)

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
            layer.set_metadata("wfs_enable_request",
                               "GetCapabilities GetFeature DescribeFeatureType")

        # Configure the layer based on information from the store.
        ds = ws.get_datastore(self.get_mra_metadata("storage"))
        ft = ds[self.get_mra_metadata("name")]

        # Configure the different fields.
        field_names = []
        for field in ft.iterfields():
            layer.set_metadatas({
                "gml_%s_alias" % field.get_name(): field.get_name(),
                "gml_%s_type" % field.get_name(): field.get_type_gml(),
                # TODO: Add gml_<field name>_precision, gml_<field name>_width
                })
            field_names.append(field.get_name())

        geometry_column = ft.get_geometry_column()
        if geometry_column == None:
            geometry_column = "geometry"
        layer.set_metadatas({
            "ows_include_items": ",".join(field_names),
            "gml_include_items": ",".join(field_names),
            "gml_geometries": geometry_column,
            "gml_%s_type" % geometry_column: ft.get_geomtype_gml(),
            # TODO: Add gml_<geometry name>_occurances,
            "wfs_srs": "EPSG:4326",
            "wfs_getfeature_formatlist": "OGRGML,SHAPEZIP",
            })

        if ft.get_fid_column() != None:
            layer.set_metadatas({
                "wfs_featureid": ft.get_fid_column(),
                "gml_featureid": ft.get_fid_column(),
                })

        plugins.extend("post_configure_vector_layer", self, ws, ds, ft, layer)


class CoverageModel(LayerModel):

    def update(self, ws, cs_name, c_name, metadata):
        ws = self.ws

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
        self.set_metadatas({
            "wms_enable_request": "!GetCapabilities !GetMap !GetFeatureInfo !GetLegendGraphic",
            "wcs_enable_request": "!GetCapabilities !DescribeCoverage !GetCoverage",
            })

        # Update mra metadatas, and make sure the mandatory ones are left untouched.
        self.update_mra_metadatas(metadata)
        self.update_mra_metadatas({"name": c_name, "type": "coverage", "storage": cs_name,
                                   "workspace": ws.name, "is_model": True})

    def configure_layer(self, ws, layer, enabled=True):
        ws = self.ws

        plugins.extend("pre_configure_raster_layer", self, ws, layer)

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
                # TODO: wfs_keywordlist, wcs_srs, wcs_getfeature_formatlist...
                })

        if enabled:
            layer.set_metadata("wcs_enable_request", "GetCapabilities GetCoverage DescribeCoverage")

        plugins.extend("post_configure_raster_layer", self, ws, layer)



class Workspace(Mapfile):

    def __init__(self, *args, **kwargs):
        Mapfile.__init__(self, *args, **kwargs)
        if self.name.endswith(".ws"):
            self.name = self.name[:-3]

    # Stores:
    def get_store(self, st_type, name):
        st_type = st_type if st_type.endswith("s") else st_type + "s"
        cparam = get_store_connection_string(self.get_store_info(st_type, name))
        if st_type == "datastores":
            return stores.Datastore(cparam)
        elif st_type == "coveragestores":
            return stores.Coveragestore(cparam)
        else:
            raise AssertionError("Unknown st_type '%s'." % st_type)

    def get_store_info(self, st_type, name):
        info = self.get_mra_metadata(st_type, {})[name].copy()
        info["name"] = name
        return info

    def iter_store_names(self, st_type):
        return self.get_mra_metadata(st_type, {}).iterkeys()

    def iter_stores(self, st_type):
        return self.get_mra_metadata(st_type, {}).iteritems()

    def create_store(self, st_type, name, configuration):
        with self.mra_metadata(st_type, {}) as stores:
            if name in stores:
                raise KeyExists(name)
            stores[name] = configuration

    def update_store(self, st_type, name, configuration):
        with self.mra_metadata(st_type, {}) as stores:
            stores[name].update(configuration)

    def delete_store(self, st_type, name):
        with self.mra_metadata(st_type, {}) as stores:
            del stores[name]

    # Datastores:

    def get_datastore(self, name):
        """Returns a store.Datastore object from the workspace."""
        return self.get_store("datastore", name)

    def get_datastore_info(self, name):
        """Returns info for a datastore from the workspace."""
        return self.get_store_info("datastore", name)

    def iter_datastore_names(self):
        """Return an iterator over the datastore names."""
        return self.iter_store_names("datastore")

    def iter_datastores(self):
        """Return an iterator over the datastore (names, configuration)."""
        return self.iter_stores("datastore")

    def create_datastore(self, name, configuration):
        """Creates a new datastore."""
        return self.create_store("datastore", name, configuration)

    def update_datastore(self, name, configuration):
        """Update a datastore."""
        return self.update_store("datastore", name, configuration)

    def delete_datastore(self, name):
        """Delete a datastore."""
        try:
            next(self.iter_featuretypemodels(name))
        except StopIteration:
            pass # No layers use our store, all OK.
        else:
            raise ValueError("The datastore '%s' can't be delete because it is used." % name)
        return self.delete_store("datastore", name)

    # Coveragestores (this is c/p from datastores):

    def get_coveragestore(self, name):
        """Returns a store.Coveragestore object from the workspace."""
        return self.get_store("coveragestore", name)

    def get_coveragestore_info(self, name):
        """Returns info for a coveragestore from the workspace."""
        return self.get_store_info("coveragestore", name)

    def iter_coveragestore_names(self):
        """Return an iterator over the coveragestore names."""
        return self.iter_store_names("coveragestore")

    def iter_coveragestores(self):
        """Return an iterator over the coveragestore (names, configuration)."""
        return self.iter_stores("coveragestore")

    def create_coveragestore(self, name, configuration):
        """Creates a new coveragestore."""
        return self.create_store("coveragestore", name, configuration)

    def update_coveragestore(self, name, configuration):
        """Update a coveragestore."""
        return self.update_store("coveragestore", name, configuration)

    def delete_coveragestore(self, name):
        """Delete a coveragestore."""
        try:
            next(self.iter_coveragemodels(name))
        except StopIteration:
            pass # No layers use our store, all OK.
        else:
            raise ValueError("The coveragestore '%s' can't be delete because it is used." % name)
        return self.delete_store("coveragestore", name)

    # LayerModels:

    def __ms2model(self, ms_layer):
        if ms_layer.name.startswith("featuretype:"):
            return FeatureTypeModel(self, ms_layer)
        elif ms_layer.name.startswith("coverage:"):
            return CoverageModel(self, ms_layer)
        else:
            raise ValueError("Badly named Layer Model '%s'." % ms_layer.name)

    def iter_layermodels(self, st_type=None, store=None, **kwargs):
        if st_type:
            kwargs.setdefault("mra", {})["type"] = st_type
        if ds_name != None:
            kwargs.setdefault("mra", {})["storage"] = ds_name
        for ms_layer in self.iter_ms_layers(*kwargs):
            yield self.__ms2model(ms_layer)

    def get_layermodel(self, st_type, store, name):
        try:
            return next(self.iter_layermodels(attr={"name":"%s:%s:%s" % (st_type, store, name)}))
        except StopIteration:
            raise KeyError((st_type, store, name))

    def has_layermodel(self, st_type, name, store):
        try:
            self.get_getlayermodel(st_type, name, store)
        except KeyError:
            return False
        else:
            return True

    def create_layermodel(self, st_type, store, name, metadata={}):
        if self.has_layermodel(st_type, store, name):
            raise KeyExists((st_type, store, name))
        ft = self.__ms2model(mapscript.layerObj(self.ms))
        ft.update(self, st_type, store, name, metadata)
        return ft

    def update_layermodel(self, st_type, store, name, metadata={}):
        ft.update(self, st_type, store, name, metadata)

    def delete_layermodel(self, st_type, ds_name, ft_name):
        model = self.get_layermodel(st_type, ds_name, ft_name)
        if model.get_mra_metadata("layers", []):
            raise ValueError("The %s '%s' can't be delete because it is used." % (st_type, ft_name))
        self.ms.removeLayer(model.ms.index)


    # Featuretypes

    def iter_featuretypemodels(self, ds_name=None, **kwargs):
        return self.iter_layermodels("featuretype", ds_name, **kwargs)

    def get_featuretypemodel(self, ds_name, ft_name):
        return self.get_layermodel("featuretype", ds_name, ft_name)

    def has_featuretypemodel(self, ds_name, ft_name):
        return self.has_layermodel("featuretype", ds_name, ft_name)

    def create_featuretypemodel(self, ds_name, ft_name, metadata={}):
        return self.create_layermodel("featuretype", ds_name, ft_name, metadata)

    def update_featuretypemodel(self, ds_name, ft_name, metadata={}):
        return self.update_layermodel("featuretype", ds_name, ft_name, metadata={})

    def delete_featuretypemodel(self, ds_name, ft_name):
        return self.delete_layermodel("featuretype", ds_name, ft_name)

    # Coverages

    def iter_coveragemodels(self, ds_name=None, **kwargs):
        return self.iter_layermodels("coverage", ds_name, **kwargs)

    def get_coveragemodel(self, ds_name, ft_name):
        return self.get_layermodel("coverage", ds_name, ft_name)

    def has_coveragemodel(self, ds_name, ft_name):
        return self.has_layermodel("coverage", ds_name, ft_name)

    def create_coveragemodel(self, ds_name, ft_name, metadata={}):
        return self.create_layermodel("coverage", ds_name, ft_name, metadata)

    def update_coveragemodel(self, ds_name, ft_name, metadata={}):
        return self.update_layermodel("coverage", ds_name, ft_name, metadata={})

    def delete_coveragemodel(self, ds_name, ft_name):
        return self.delete_layermodel("coverage", ds_name, ft_name)


# Finaly the global context:

class MRA(object):
    def __init__(self, config_path):
        try:
            self.config = yaml.load(open(config_path, "r"))
        except yaml.YAMLError as e:
            exit("Error in configuration file: %s" % e)

    def safe_path_join(self, root, *args):
        full_path = os.path.realpath(os.path.join(root, *args))
        if not full_path.startswith(os.path.realpath(root)):
            raise webapp.Forbidden(message="path '%s' outside root directory." % (args))
        return full_path

    def mk_path(self, path):
        dirs = os.path.dirname(path)
        if not os.path.isdir(dirs):
            os.makedirs(dirs)
        return path

    def get_path(self, *args):
        root = self.config["storage"]["root"]
        return self.safe_path_join(root, *args)

    def get_resouces_path(self, *args):
        root = self.config["storage"].get("resources", "resources")
        return self.get_path(root, *args)

    # Styles:

    def get_style_path(self, *args):
        root = self.config["storage"].get("styles", "styles")
        return self.get_resouces_path(root, *args)

    # Files:

    def get_file_path(self, *args):
        root = self.config["storage"].get("data", "data")
        return self.get_resouces_path(root, *args)

    # Available (get):

    def get_available_path(self, *args):
        root = self.config["storage"].get("available", "available")
        return self.get_path(root, *args)

    def get_available(self):
        path = self.get_available_path("layers.map")
        # TODO: Create the thing if not existing.
        return Mapfile(path)

    # Workspaces:

    def list_workspaces(self):
        for (root, subFolders, files) in os.walk(self.get_available_path()):
            for f in files:
                if f.endswith(".ws.map") and not f.startswith('.'):
                    yield f[:-7]

    def create_workspace(self, name):
        path = self.get_available_path("%s.ws.map" % name)
        return Workspace(self.mk_path(path), create=True)

    def get_workspace(self, name):
        path = self.get_available_path("%s.ws.map" % name)
        return Workspace(path)

    def delete_workspace(self, name):
        path = self.get_available_path("%s.ws.map" % name)


    # Services:

    def get_service_path(self, *args):
        root = self.config["storage"].get("services", "services")
        return self.get_path(root, *args)

    def get_services(self):
        pass

    def get_service(self, name):
        path = self.get_service_path("%s.map" % name)
        return Mapfile(path)
