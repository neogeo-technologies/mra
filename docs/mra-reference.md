# MapServer REST API Resources

This section describes the REST configuration API.

It is in process of writing...

### Compatibility with GeoServer REST API

MapServer REST API was designed to offer compatibility with the GeoServer REST API model because we believe that both should be able to communicate.
These two concepts should not be viewed as being mutually opposed.
On the contrary, they can be mutually rewarding. This was helpful for us. So this can be used more widely.

The pre-existence of GeoServer REST API obliges us to make choices, and hence depart from the MapServer logic in favor of the GeoServer model.
That does not mean to say that it would be the best way to control MapServer.
However, despite the substantial differences between the two softwares, MapServer REST API help to a certain extent to reduce the gap.

MapServer REST API is not fully compatible with GeoServer.
Either do we believe that it makes much sense to include elements which does not affect the good functioning of services provided.


### Mapfiles & Workspaces, data stores, featuretypes, coverage stores, coverages

In GeoServer, a workspace is a grouping of data stores and coverage stores.

A data store is a source of spatial data that is vector based.
It can be a file such as a _shapefile_ or a database such as _PostGIS_.
A data store contains one or more feature types which are vector based spatial resource.
In cases of a _shapefile_, the feature type is unique and corresponds to the data store.
In cases of a _PostGIS_ database, feature types corresponds to tables.

A coverage store is a source of spatial data that is raster based.
It can be a _GeoTIFF_ file and for this format file, the coverage is unique and corresponds to the coverage store.

The concept of _workspace_ comes from GeoServer and it does not exist in MapServer.
This is the main difference between the two designs.

However, it is possible to assimilate this concept to a single _mapfile_.
So a MapServer' _mapfile_ is assimilated to GeoServer' _workspace_.
And this contains layers which shall be regarded as connections to data stores or to coverage stores.
That can be treated as a [layer](#layers) and that can be published as [OGC Web Service](#ogc-web-services) or not.

###### Workspaces

Resource | Description
---------|------------
[**GET    workspaces**](resources/get-workspaces.md) | Returns a list containing workspaces.
[**POST   workspaces**](resources/post-workspaces.md) | Creates a new workspace.
[**GET    workspaces/\<ws\>**](resources/get-workspace.md) | Returns workspace \<ws\>.

###### Data Stores

Resource | Description
---------|------------
[**GET    workspaces/\<ws\>/datastores**](resources/get-datastores.md) | Returns a list containing data stores in the workspace \<ws\>.
[**POST   workspaces/\<ws\>/datastores**](resources/post-datastores.md) | Creates a new data store.
[**GET    workspaces/\<ws\>/datastores/\<ds\>**](resources/get-datastore.md) | Returns data store \<ds\>.
[**PUT    workspaces/\<ws\>/datastores/\<ds\>**](resources/put-datastore.md) | Modifies data store \<ds\>.
[**DELETE workspaces/\<ws\>/datastores/\<ds\>**](resources/delete-datastore.md) | Deletes data store \<ds\>.
[**PUT    workspaces/\<ws\>/datastores/\<ds\>/file\<.extension\>**](resources/put-datastore-file.md) | Uploads a vector data file from a local source.

###### Feature Types

Resource | Description
---------|------------
[**GET    workspaces/\<ws\>/datastores/\<ds\>/featuretypes**](resources/get-featuretypes.md) | Returns a list containing all feature types in data store \<ds\>.
[**POST   workspaces/\<ws\>/datastores/\<ds\>/featuretypes**](resources/post-featuretypes.md) | Creates a new feature type. It creates the associated layer by default.
[**GET    workspaces/\<ws\>/datastores/\<ds\>/featuretypes/\<ft\>**](resources/get-featuretype.md) | Returns feature type \<ft\>.
[**PUT    workspaces/\<ws\>/datastores/\<ds\>/featuretypes/\<ft\>**](resources/put-featuretype.md) | Modifies feature type  \<ft\>.
[**DELETE workspaces/\<ws\>/datastores/\<ds\>/featuretypes/\<ft\>**](resources/delete-featuretype.md) | Delete feture type \<ft\>.

###### Coverage Stores

Resource | Description
---------|------------
[**GET    workspaces/\<ws\>/coveragestores**](resources/get-coveragestores.md) | Returns a list containing coverage stores in the workspace \<ws\>.
[**POST   workspaces/\<ws\>/coveragetores**](resources/post-coveragestores.md) | Creates a new coverage store.
[**GET    workspaces/\<ws\>/coveragestores/\<cs\>**](resources/get-coveragestore.md) | Returns coverage store \<cs\>.
[**PUT    workspaces/\<ws\>/coveragestores/\<cs\>**](resources/put-coveragestore.md) | Modifies coverage store \<cs\>.
[**DELETE workspaces/\<ws\>/coveragestores/\<cs\>**](resources/delete-coveragestore.md) | Deletes coverage store \<cs\>.
[**PUT    workspaces/\<ws\>/coveragestores/\<cs\>/file\<.extension\>**](resources/put-coveragestore-file.md) | Uploads a raster data file from a local source.

###### Coverages

Resource | Description
---------|------------
[**GET    workspaces/\<ws\>/coveragestores/\<cs\>/coverages**](resources/get-coverages.md) | Returns a list containing all coverages in coverage store \<cs\>.
[**POST   workspaces/\<ws\>/coveragestores/\<cs\>/coverages**](resources/post-coverages.md) | Creates a new coverage. It creates the associated layer by default.
[**GET    workspaces/\<ws\>/coveragestores/\<cs\>/coverages/\<c\>**](resources/get-coverage.md) | Returns coverage \<c\>.
[**PUT    workspaces/\<ws\>/coveragestores/\<cs\>/coverages/\<c\>**](resources/put-coverage.md) | Modifies coverage \<c\>.
[**DELETE workspaces/\<ws\>/coveragestores/\<cs\>/coverages/\<c\>**](resources/delete-coverage.md) | Deletes coverage \<c\>.


### Styles

A style describes how a resource (a feature type or a coverage) should be symbolized or rendered by a WMS.

Resource | Description
---------|------------
[**GET    styles**](resources/get-styles.md) | Returns a list containing all available styles.
[**POST   styles**](resources/post-styles.md) | Creates a new style.
[**GET    styles/\<s\>**](resources/get-style.md) | Returns style \<s\>.
[**PUT    styles/\<s\>**](resources/put-style.md) | Modifies style \<s\>.
[**DELETE styles/\<s\>**](resources/delete-style.md) | Deletes style \<s\>.


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
[**GET    layers/\<l\>**](resources/get-layer.md) | Returns layer \<l\>.
[**PUT    layers/\<l\>**](resources/put-layer.md) | Modifies layer \<l\>.
[**DELETE layers/\<l\>**](resources/delete-layer.md) | Deletes layer \<l\>.
[**GET    layers/\<l\>/styles**](resources/get-layerstyles.md) | Returns a list containing all styles associated to layer \<l\>.
[**DELETE layers/\<l\>/styles/\<s\>**](resources/get-layerstyle.md) | Removes style \<s\> from layer \<l\>.
[**GET    layers/\<l\>/fields**](resources/get-layerfields.md) | Returns a list containing all fields associated to layer \<l\>.


### Layer groups

A layergroup is a grouping of layers and styles that can be accessed as a single layer in a WMS GetMap request.

Resource | Description
---------|------------
[**GET    layergroups**](resources/get-layergroups.md) | Returns a list containing all existing layer groups.
[**POST   layergroups**](resources/post-layergroups.md) | Creates a new layer group.
[**GET    layergroups/\<lg\>**](resources/get-layergroup.md) | Returns layer group \<lg\>.
[**PUT    layergroups/\<lg\>**](resources/put-layergroup.md) | Modifies layer group \<lg\> (i.e. adding or removing layers of the group).
[**DELETE layergroups/\<lg\>**](resources/delete-layergroup.md) | Deletes layer group \<lg\>.


### OGC Web Services

Controls the settings of OWS services (available for WMS, WFS and WCS).

Resource | Description
---------|------------
[**GET    service/[wms,wfs,wcs]/setting**](resources/get-ogc-settings.md) | Returns the status of the OGC service.
[**PUT    service/[wms,wfs,wcs]/setting**](resources/put-ogc-settings.md) | Enables or disables the OGC service.
