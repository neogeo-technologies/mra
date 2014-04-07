# MapServer REST API Resources

This section describes the REST configuration API.

It is in process of writing...
Nevertheless, you could refer to the GeoServer Rest API documentation cause MRA was designed to offer compatibility with this model.
You will also find few _docstrings_ by reading the code, especially the module `server.py` which defines the URL mapping infrastructure and HTTP methods used by the REST API.


### Workspaces, data stores & featuretypes, coverage stores & coverages

A workspace is a grouping of data stores and coverage stores.

A data store is a source of spatial data that is vector based.
It can be a file such as a _shapefile_ or a database such as _PostGIS_.
A data store contains one or more feature types which are vector based spatial resource.
In cases of a _shapefile_, the feature type is unique and corresponds to the data store.
In cases of a _PostGIS_ database, feature types corresponds to tables.

A coverage store is a source of spatial data that is raster based. 
In current version, it can only be a _GeoTIFF_ file.
For this format file, the coverage is unique and corresponds to the coverage store.

Resource | Description
---------|------------
[**GET    workspaces**](resources/get-workspaces.md) | Returns a list containing workspaces.
[**POST   workspaces**](resources/post-workspaces.md) | Creates a new workspace.
[**GET    workspaces/_ws_**](resources/get-workspace.md) | Returns workspace `_ws_'.
~ | ~
[**GET    workspaces/_ws_/datastores**](resources/get-datastores.md) | Returns a list containing data stores in the workspace `_ws_'.
[**POST   workspaces/_ws_/datastores**](resources/post-datastores.md) | Creates a new data store.
[**GET    workspaces/_ws_/datastores/_ds_**](resources/get-datastore.md) | Returns data store `_ds_'.
[**PUT    workspaces/_ws_/datastores/_ds_**](resources/put-datastore.md) | Modifies data store `_ds_'.
[**DELETE workspaces/_ws_/datastores/_ds_**](resources/delete-datastore.md) | Deletes data store `_ds_'.
[**PUT    workspaces/_ws_/datastores/_ds_/file_.extension_**](resources/put-datastore-file.md) | Uploads a vector data file from a local source.
~ | ~
[**GET    workspaces/_ws_/datastores/_ds_/featuretypes**](resources/get-featuretypes.md) | Returns a list containing all feature types in data store `_ds_'.
[**POST   workspaces/_ws_/datastores/_ds_/featuretypes**](resources/post-featuretypes.md) | Creates a new feature type. It creates the associated layer by default.
[**GET    workspaces/_ws_/datastores/_ds_/featuretypes/_ft_**](resources/get-featuretype.md) | Returns feature type `_ft_'.
[**PUT    workspaces/_ws_/datastores/_ds_/featuretypes/_ft_**](resources/put-featuretype.md) | Modifies feature type  `_ft_'.
[**DELETE workspaces/_ws_/datastores/_ds_/featuretypes/_ft_**](resources/delete-featuretype.md) | Delete feture type `_ft_'.
~ | ~
[**GET    workspaces/_ws_/coveragestores**](resources/get-coveragestores.md) | Returns a list containing coverage stores in the workspace `_ws_'.
[**POST   workspaces/_ws_/coveragetores**](resources/post-coveragestores.md) | Creates a new coverage store.
[**GET    workspaces/_ws_/coveragestores/_cs_**](resources/get-coveragestore.md) | Returns coverage store `_cs_'.
[**PUT    workspaces/_ws_/coveragestores/_cs_**](resources/put-coveragestore.md) | Modifies coverage store `_cs_'.
[**DELETE workspaces/_ws_/coveragestores/_cs_**](resources/delete-coveragestore.md) | Deletes coverage store `_cs_'.
[**PUT    workspaces/_ws_/coveragestores/_cs_/file_.extension_**](resources/put-coveragestore-file.md) | Uploads a raster data file from a local source.
~ | ~
[**GET    workspaces/_<ws>_/coveragestores/_cs_/coverages**](resources/get-coverages.md) | Returns a list containing all coverages in coverage store `_cs_'.
[**POST   workspaces/_<ws>_/coveragestores/_cs_/coverages**](resources/post-coverages.md) | Creates a new coverage. It creates the associated layer by default.
[**GET    workspaces/_<ws>_/coveragestores/_cs_/coverages/_c_**](resources/get-coverage.md) | Returns coverage `_c_'.
[**PUT    workspaces/_<ws>_/coveragestores/_cs_/coverages/_c_**](resources/put-coverage.md) | Modifies coverage `_c_'.
[**DELETE workspaces/_<ws>_/coveragestores/_cs_/coverages/_c_**](resources/delete-coverage.md) | Deletes coverage `_c_'.


### Styles

A style describes how a resource (a feature type or a coverage) should be symbolized or rendered by a WMS.

Resource | Description
---------|------------
[**GET    styles**](resources/get-styles.md) | Returns a list containing all available styles.
[**POST   styles**](resources/post-styles.md) | Creates a new style.
[**GET    styles/_s_**](resources/get-style.md) | Returns style `_s_'.
[**PUT    styles/_s_**](resources/put-style.md) | Modifies style `_s_'.
[**DELETE styles/_s_**](resources/delete-style.md) | Deletes style `_s_'.


### Fonts

Configures available fonts.

Resource | Description
---------|------------
[**GET    fonts**](resources/get-fonts.md) | Returns the list of available fonts.
[**PUT    fonts**](resources/put-fonts.md) | Uploads fonts from a local source.


### Layers

A layer is a data resource that could be published by a OGC Web Service.
So a layer is the combination of data (feature type or coverage) plus styling.

Resource | Description
---------|------------
[**GET    layers**](resources/get-layers.md) | Returns a list containing all layers.
[**POST   layers**](resources/post-layers.md) | Creates a new layer.
[**GET    layers/_l_**](resources/get-layer.md) | Returns layer `_l_'.
[**PUT    layers/_l_**](resources/put-layer.md) | Modifies layer `_l_'.
[**DELETE layers/_l_**](resources/delete-layer.md) | Deletes layer `_l_'.
[**GET    layers/_l_/styles**](resources/get-layerstyles.md) | Returns a list containing all styles associated to layer `_l_'.
[**DELETE layers/_l_/styles/_s_**](resources/get-layerstyle.md) | Removes style `_s_' from layer `_l_'.
[**GET    layers/_l_/fields**](resources/get-layerfields.md) | Returns a list containing all fields associated to layer `_l_'.


### Layer groups

A layergroup is a grouping of layers and styles that can be accessed as a single layer in a WMS GetMap request.

Resource | Description
---------|------------
[**GET    layergroups**](resources/get-layergroups.md) | Returns a list containing all existing layer groups.
[**POST   layergroups**](resources/post-layergroups.md) | Creates a new layer group.
[**GET    layergroups/_lg_**](resources/get-layergroup.md) | Returns layer group `_lg_'.
[**PUT    layergroups/_lg_**](resources/put-layergroup.md) | Modifies layer group `_lg_' (i.e. adding or removing layers of the group).
[**DELETE layergroups/_lg_**](resources/delete-layergroups.md) | Deletes layer group `_lg_'.


### OGC Web Services

Controls the settings of OWS services (available for WMS, WFS and WCS).

Resource | Description
---------|------------
[**GET    service/[wms,wfs,wcs]/setting**](resources/get-ogc-settings.md) | Returns the status of the OGC service.
[**PUT    service/[wms,wfs,wcs]/setting**](resources/put-ogc-settings.md) | Enables or disables the OGC service.
