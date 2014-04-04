# MapServer REST API Resources

This section describes the REST configuration API.

It is in process of writing...
Nevertheless, you could refer to the GeoServer Rest API documentation cause MRA was designed to offer compatibility with this model.
You will also find few _docstrings_ by reading the code, especially the module `server.py` which defines the URL mapping infrastructure and HTTP methods used by the REST API.

### Workspaces

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
[**GET    workspaces**](pages/workspaces.md#get-workspaces) | Returns a list containing workspaces.
[**POST    workspaces**](pages/workspaces.md#post-workspaces) | Creates a new workspace.
[**GET    workspaces/_{ws}_**](pages/workspaces.md#get-workspaces-ws) | Returns the given workspace.
[**GET    workspaces/_{ws}_/datastores**](pages/datastores.md#get-datastores) | Returns a list containing data stores in the given workspace.
[**POST   workspaces/_{ws}_/datastores**](pages/datastores.md#post-datastores) | Creates  a new data store.
[**GET    workspaces/_{ws}_/datastores/_{ds}_**](pages/datastores.md#get-datastores-ds) | Returns data store _{ds}_.
[**PUT    workspaces/_{ws}_/datastores/_{ds}_**](pages/datastores.md#put-datastores-ds) | Modifies data store _{ds}_.
[**DELETE workspaces/_{ws}_/datastores/_{ds}_**](pages/datastores.md#delete-datastores-ds) | Deletes data store _{ds}_.
[**PUT    workspaces/_{ws}_/datastores/_{ds}_/file._{extension}_**](pages/datastores.md#put-datastores-ds-file-extension) | Uploads a vector data file from a local source.
**GET    workspaces/_{ws}_/datastores/_{ds}_/featuretypes** | Returns a list containing all feature types in selected data store.
**POST   workspaces/_{ws}_/datastores/_{ds}_/featuretypes** | Creates a new feature type. It creates the associated layer by default.
**GET    workspaces/_{ws}_/datastores/_{ds}_/featuretypes/_{ft}_** | Returns feature type _{ft}_.
**PUT    workspaces/_{ws}_/datastores/_{ds}_/featuretypes/_{ft}_** | Modifies feature type  _{ft}_.
**DELETE workspaces/_{ws}_/datastores/_{ds}_/featuretypes/_{ft}_** | Delete feture type _{ft}_.
**GET    workspaces/_{ws}_/coveragestores** | Returns a list containing coverage stores in the given workspace.
**POST   workspaces/_{ws}_/coveragetores** | Creates a new coverage store.
**GET    workspaces/_{ws}_/coveragestores/_{cs}_** | Returns coverage store _{cs}_.
**PUT    workspaces/_{ws}_/coveragestores/_{cs}_** | Modifies coverage store _{ds}_.
**DELETE workspaces/_{ws}_/coveragestores/_{cs}_** | Deletes coverage store _{ds}_.
**PUT    workspaces/_{ws}_/coveragestores/_{cs}_/file._{extension}_** | Uploads a raster data file from a local source.
**GET    workspaces/_{ws}_/coveragestores/_{cs}_/coverages** | Returns a list containing all coverages in selected coverage store.
**POST   workspaces/_{ws}_/coveragestores/_{cs}_/coverages** | Creates a new coverage. It creates the associated layer by default.
**GET    workspaces/_{ws}_/coveragestores/_{cs}_/coverages/_{c}_** | Returns coverage _{c}_.
**PUT    workspaces/_{ws}_/coveragestores/_{cs}_/coverages/_{c}_** | Modifies coverage _{c}_.
**DELETE workspaces/_{ws}_/coveragestores/_{cs}_/coverages/_{c}_** | Deletes coverage _{c}_.

### Styles

A style describes how a resource (a feature type or a coverage) should be symbolized or rendered by a Web Map Service.
Styles are specified with SLD.

Resource | Description
---------|------------
**GET    styles** | Returns a list containing all SLD styles.
**POST   styles** | Creates a new SLD style.
**GET    styles/_{s}_** | Returns style _{s}_.
**PUT    styles/_{s}_** | Modifies style _{s}_.
**DELETE styles/_{s}_** | Deletes style _{s}_.


### Layers

A layer is a data resource that could be published by a OGC Web Service.
So a layer is the combination of data (feature type or coverage) plus styling (in case of OGC:WMS).

Resource | Description
---------|------------
**GET    layers** | Returns a list containing all layers.
**POST   layers** | Creates a new layer.
**GET    layers/_{l}_** | Returns layer _{l}_.
**PUT    layers/_{l}_** | Modifies layer _{l}_.
**DELETE layers/_{l}_** | Deletes layer _{l}_.
**GET    layers/_{l}_/styles** | Returns a list containing all styles associated to layer _{l}_.
**DELETE layers/_{l}_/styles/_{s}_** | Removes style _{s}_ from layer _{l}_.
**GET    layers/_{l}_/fields** | Returns a list containing all fields associated to layer _{l}_.


### Layer groups

A layergroup is a grouping of layers and styles that can be accessed as a single layer in a OGC:WMS GetMap request.

Resource | Description
---------|------------
**GET    layergroups** | Returns a list containing all existing layer groups.
**POST   layergroups** | Creates a new layer group.
**GET    layergroups/_{lg}_** | Returns layer group _{lg}_.
**PUT    layergroups/_{lg}_** | Modifies layer group _{lg}_.
**DELETE layergroups/_{lg}_** | Delete layer group _{lg}_.


### OGC Web Services

Controls the settings of OWS services (available for OGC:WMS, OGC:WFS and OGC:WCS).

Resource | Description
---------|------------
**GET    service/[wms,wfs,wcs]/setting** | Returns the status of the main OGC service.
**PUT    service/[wms,wfs,wcs]/setting** | Enables or disables the main OGC service.

### Fonts

Configures available fonts.

Resource | Description
---------|------------
**GET    fonts** | Returns the list of available fonts.
**PUT    fonts** | Uploads fonts from a local source.
