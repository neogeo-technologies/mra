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

from osgeo import ogr, osr, gdal
import mapscript
import tools

class Extent(list):

    def __init__(self, *args, **kwargs):
        if len(args) == 4:
            args = [args]
        list.__init__(self, *args, **kwargs)

    def minX(self):
        return self[0]

    def minY(self):
        return self[1]

    def maxX(self):
        return self[2]

    def maxY(self):
        return self[3]

    def addX(self, *args):
        for x in args:
            self[0] = min(self[0], x)
            self[2] = max(self[2], x)

    def addY(self, *args):
        for y in args:
            self[1] = min(self[1], y)
            self[3] = max(self[3], y)


class Field(object):
    """A Field implementation backed by ogr."""

    @staticmethod
    def type_name(i):
        # This is ugly, but this should really be static and it seems like
        # swig doesnt handle that when generating gdal/ogr bindings :(
        ogr.FieldDefn.GetFieldTypeName(ogr.FieldDefn(), 0)

    def __init__(self, backend, layer):
        """backend should be a ogr.FieldDefn object which will be used to retrieve data.
        """

        self.backend = backend
        self.layer = layer
        self.nullable = layer.nullables.get(self.get_name(), True)

    def get_justify(self):
        return self.backend.GetJustify()

    def get_name(self):
        return self.backend.GetName()

    def get_precision(self):
        return self.backend.GetPrecision()

    def get_type(self):
        return self.backend.GetType()

    def get_type_name(self):
        return self.backend.GetTypeName()

    def get_type_gml(self):
        type = self.get_type()
        if type in (0, 1):
            return 'Integer'
        if type in (2, 3):
            return 'Real'
        if type in (4, 5):
            return 'Character'
        if type in (6, 7):
            return 'Unknown' #:)
        if type in (9, 10):
            return 'Date'
        else:
            return 'Unknown'

    def get_width(self):
        return self.backend.GetWidth()

    def is_nullable(self):
        return self.nullable


class Feature(object):
    """A Feature implementation backed by ogr."""

    def __init__(self, backend, layer):
        """backend should be a ogr.Feature object which will be used to retrieve data.
        """

        self.backend = backend
        self.layer

    def __getattr__(self, attr):
        return self[attr]

    def __getitem__(self, idx):
        if not isinstance(idx, int):
            idx = self.backend.GetFieldIndex(idx)
            if idx < 0: raise KeyError()
        return self.backend.GetField(idx)

    def get_id(self):
        return self.backend.GetFID()

    def get_field(self):
        return Field(self.backend.GetFieldDefn(), layer)


class Featuretype(object):
    """A featuretype implementation backed by ogr."""

    @staticmethod
    def geomtype_name(i):
        return ogr.GeometryTypeToName(i)

    def __init__(self, backend, ds, no_aditional_info=False):
        """backend should be a ogr.Layer object which will be used to retrieve data.
        """

        self.backend = backend
        self.ds = ds

        self.nullables = {}
        if not no_aditional_info:
            self.get_aditional_info()


    def __len__(self):
        return self.nbfeatures()

    def __iter__(self):
        return self.iterfeatures()

    def get_name(self):
        return self.backend.GetName()

    def get_fid_column(self):
        if self.backend.GetFIDColumn() == "":
            return None
        return self.backend.GetFIDColumn()

    def get_geometry_column(self):
        if self.backend.GetGeometryColumn() == "":
            return None
        return self.backend.GetGeometryColumn()

    def get_extent(self):
        minX, maxX, minY, maxY = self.backend.GetExtent()
        return Extent(minX, minY, maxX, maxY)

    def get_geomtype(self):
        gtype = self.backend.GetGeomType()
        if gtype != 0:
            return gtype
        # We didnt find anything. This is *probably* an error in POSTGIS,
        # for example GEOMTRY.
        # TODO: Don't fall back on POLYGON ...
        return ogr.wkbPolygon

    def get_geomtype_name(self):
        gtype = self.get_geomtype()
        return ogr.Geometry(gtype).GetGeometryName()

    def get_geomtype_mapscript(self):
        ogr_geometry = self.get_geomtype_name()
        if ogr_geometry in ('POINT', 'MULTIPOINT'):
            return mapscript.MS_LAYER_POINT
        if ogr_geometry in ('LINESTRING','MULTILINESTRING'):
            return mapscript.MS_LAYER_LINE
        if ogr_geometry in ('MULTIPOLYGON','POLYGON'):
            return mapscript.MS_LAYER_POLYGON
        else:
            raise KeyError('Unrecognized geometry \'%s\'' % ogr_geometry)

    def get_geomtype_gml(self):
        ogr_geometry = self.get_geomtype_name()
        if ogr_geometry == 'POINT':
            return ogr_geometry.lower()
        if ogr_geometry == 'MULTIPOINT':
            return ogr_geometry.lower()
        if ogr_geometry == 'LINESTRING':
            return 'line'
        if ogr_geometry == 'MULTILINESTRING':
            return 'multiline'
        if ogr_geometry == 'POLYGON':
            return ogr_geometry.lower()
        if ogr_geometry == 'MULTIPOLYGON':
            return ogr_geometry.lower()
        else:
            raise KeyError('Unrecognized geometry \'%s\'' % ogr_geometry)

    def get_geomtype_wkb(self):
        return Featuretype.geomtype_name(self.get_geomtype())

    def get_authority(self):
        # This is ugly, still looking for something better.
        proj4 = osr.SpatialReference()
        proj4.ImportFromProj4(self.backend.GetSpatialRef().ExportToProj4())
        return proj4.GetAuthorityName(None), proj4.GetAuthorityCode(None)

    def get_authority_name(self):
        return self.get_authority()[0]

    def get_authority_code(self):
        return self.get_authority()[1]

    def get_projection(self):
        return "%s:%s" % self.get_authority()

    def get_proj4(self):
        return self.backend.GetSpatialRef().ExportToProj4()

    def get_wkt(self):
        return self.backend.GetSpatialRef().ExportToWkt()

    def get_latlon_extent(self):
        rect = mapscript.rectObj(*self.get_extent())
        res = rect.project(mapscript.projectionObj(self.get_proj4()),
                           mapscript.projectionObj('+init=epsg:4326'))

        return Extent(rect.minx, rect.miny, rect.maxx, rect.maxy)

    def get_native(self):
        return str(self.backend.GetSpatialRef())

    def fieldindex(self, field):
        idx = GetLayerDefn().GetFieldIndex(field)
        if idx < 0:
            raise AttributeError()
        return idx

    def nbfields(self):
        return self.backend.GetFieldCount()

    def fields(self):
        return list(self.iterfields())

    def iterfields(self):
        for i in xrange(self.backend.GetLayerDefn().GetFieldCount()):
            yield Field(self.backend.GetLayerDefn().GetFieldDefn(i), self)

    def nbfeatures(self):
        return self.backend.GetFeatureCount()

    def iterfeatures(self, what=[], when={}):
        if what != [] or when != {}:
            raise NotImplementedError("iterfeature doesn't support filters yet.")
        for i in xrange(self.backend.GetFeatureCount()):
            yield Feature(self.backend.GetFeature(i), self)

    def get_aditional_info(self):

        tokens = self.get_name().split('.', 2)
        if len(tokens) < 2:
            tokens.insert(0, 'public')
        schema, table = tokens

        result = self.ds.backend.ExecuteSQL("SELECT column_name, is_nullable FROM INFORMATION_SCHEMA.COLUMNS "
                                         "WHERE table_schema = '%s' AND table_name = '%s'" %
                                         (schema, table))

        if not result: return

        for i in xrange(result.GetFeatureCount()):
            feature = result.GetFeature(i)
            name, nullable = feature.GetField(0), feature.GetField(1)
            self.nullables[name] = nullable


class Datastore(object):
    """A datastore implementation backed by ogr."""

    def __init__(self, path):
        """Path will be used to open the store, it can be a simple filesystem path
        or something more complex used by gdal/ogr to access databases for example.

        The first argument to __init__ can also directly be a gdal/ogr object.
        """
        self.backend = path if isinstance(path, ogr.DataSource) else ogr.Open(path)
        if self.backend == None:
            raise ValueError("Datastore backend could not be opened using '%s'." % path)

    def __len__(self):
        return self.nblayers()

    def __iter__(self):
        return self.iterlayers()

    def __contains__(self, key):
        try:
            self[item]
        except LookupError:
            return False
        return True

    def __getitem__(self, key):
        if isinstance(key, int):
            item = self.backend.GetLayerByIndex(key)
            if item == None: raise IndexError("No layer '%s'" % key)
        else:
            item = self.backend.GetLayerByName(key.encode('ascii', 'ignore'))
            if item == None: raise KeyError(key)
        return Featuretype(item, self)

    def nblayers(self):
        return self.backend.GetLayerCount()

    def iterlayers(self):
        for i in xrange(self.backend.GetLayerCount()):
            yield Featuretype(self.backend.GetLayerByIndex(i), self)


class Band(object):
    """A band immplementation backed by gdal."""

    def __init__(self, backend):
        """backend should be a gdal.Band object which will be used to retrieve data.
        """

        self.backend = backend


class Coveragestore(object):
    """A coveragestore implementation backed by gdal."""

    def __init__(self, path):
        """Path will be used to open the store, it can be a simple filesystem path
        or something more complex used by gdal/ogr to access databases for example.

        The first argument to __init__ can also directly be a gdal/ogr object.
        """

        self.backend = path if isinstance(path, gdal.Dataset) else gdal.Open(path)
        if self.backend == None:
            raise ValueError("Coveragestore backend could not be opened. '%s'." % path)

    def __len__(self):
        return self.nbbands()

    def __iter__(self):
        return self.iterbands()

    def __contains__(self, idx):
        return 0 < idx and idx < self.backend.RasterCount

    def __getitem__(self, idx):
        band = self.backend.GetRasterBand(idx)
        if band == None:
            raise IndexError()
        return band

    def get_geotransform(self):
        return self.backend.GetGeoTransform()

    def get_corners(self):
        gt = self.backend.GetGeoTransform()
        corners = set()
        for x in (0, self.backend.RasterXSize):
            for y in (0, self.backend.RasterYSize):
                corners.add((gt[0]+(x*gt[1])+(y*gt[2]), gt[3]+(x*gt[4])+(y*gt[5])))
        return corners

    def get_extent(self):
        corners = self.get_corners()
        minX = min(x for x, y in corners)
        minY = min(y for x, y in corners)
        maxX = max(x for x, y in corners)
        maxY = max(y for x, y in corners)
        return Extent(minX, minY, maxX, maxY)

    def get_latlon_extent(self):
        rect = mapscript.rectObj(*self.get_extent())
        res = rect.project(mapscript.projectionObj(self.get_proj4()),
                           mapscript.projectionObj('+init=epsg:4326'))

        return Extent(rect.minx, rect.miny, rect.maxx, rect.maxy)

    def get_projection(self):
        return self.backend.GetProjection()

    def get_proj4(self):
        return tools.wkt_to_proj4(self.get_projection())

    def nbbands(self):
        return self.backend.RasterCount

    def bands(self):
        return list(self.iterbands())

    def iterbands(self):
        for i in xrange(1, self.backend.RasterCount + 1):
            yield Band(self.backend.GetRasterBand(i))
