## Data stores & Feature types

A data store is a source of spatial data that is vector based.

A data store is a connection to a data source as implied by OGR library.
It could be a shapefile, a PostGIS database or any other data type supported by OGR.

A feature type is a data set that originates from a data store.


### GET workspaces/{ws}/datastores

Returns a list containing data stores in workspace.

#### Resource URL

http://hostname/workspaces/{ws}/datastores{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**GET** http://hostname/workspaces/my_workspace/datastores.json

#### Response

**Status code:** `200 OK`

	{
	    "dataStores": [
	        {
	            "href": "http://hostname/workspaces/my_workspace/datastores/my_fisrt_datastore.json",
	            "name": "my_fisrt_datastore"
	        }
	        {
	            "href": "http://hostname/workspaces/my_workspace/datastores/my_second_datastore.json",
	            "name": "my_second_datastore"
	        }
	    ]
	}


### POST workspaces/{ws}/datastores

Creates a new data store in workspace.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}{.extension}

#### Available formats

JSON, XML.

#### Example request

**POST** http://hostname/workspaces/my_workspace/datastores.json

**POST Content-type:** `application-json`

**POST data:**

	{
	    "dataStore": {
	        "name": "pg_sample",
	        "enabled": true,
	        "connectionParameters": {
	            "host": "127.0.0.1",
	            "user": "postgres",
	            "database": "dbname",
	            "dbtype": "postgis",
	            "password": "postgres",
	            "port": "5432"
	        }
	    }
	}

#### Response

**Status code:** `201 Created`

**Location:** `http://hostname/workspaces/my_workspace/datastores/pg_sample.json`


### GET workspaces/{ws}/datastores/{ds}

Returns data store {ds}.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Example request

**GET** http://hostname/workspaces/my_workspace/datastores/pg_sample.json

#### Response

**Status code:** `200 OK`

	{
	    "dataStore": {
	        "name": "pg_sample",
	        "enabled": true,
	        "connectionParameters": {
	            "dbtype": "postgis",
	            "host": "127.0.0.1",
	            "port": "5432",
	            "database": "my_dbname",
	            "user": "postgres",
	            "password": "postgres"
	        },
	        "featureTypes": {
	            "href": "http://hostname/workspaces/my_workspace/datastores/pg_sample/featuretypes.json"
	        },
	        "workspace": {
	            "href": "http://hostname/workspaces/my_workspace.json",
	            "name": "my_workspace"
	        }
	    }
	}


### PUT workspaces/{ws}/datastores/{ds}

Modifies data store {ds}.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}{.extension}

#### Available formats

JSON, XML.

#### Example request

**PUT http://hostname/workspaces/my_workspace/datastores/pg_sample.json

**PUT Content-type:** `application-json`

**PUT Data:**

	{
	    "dataStore": {
	        "name": "pg_sample",
	        "enabled": false,
	        "connectionParameters": {
	            "dbtype": "postgis",
	            "host": "127.0.0.1",
	            "port": "5432",
	            "database": "my_dbname",
	            "user": "mra",
	            "password": "foo"
	        },
	    }
	}

#### Response

**Status code:** `201 Created`

**Location:** `http://hostname/workspaces/my_workspace/datastores/pg_sample.json`


### DELETE workspaces/{ws}/datastores/{ds}

Deletes data store {ds}.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}{.extension}

#### Available formats

JSON, XML.

#### Example request

**DELETE** http://hostname/workspaces/my_workspace/datastores/pg_sample.json

#### Response

**Status code:** `200 OK`


### PUT workspaces/{ws}/datastores/{ds}/file{.extension}

Uploads a file from a local source and creates the data store.
File must be zipped.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}/file{.extension}

#### Available formats

SHP (ShapeFile).

#### Example request

**PUT** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/file.shp

**PUT Content-type:** `application-zip`

**PUT binary-data**

#### Response

**Status code:** `200 OK`


### GET workspaces/{ws}/datastores/{ds}/featuretypes

Returns all feature type in data store.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}/featuretypes{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Example request

**GET** http://hostname/workspaces/my_workspace/datastores/my_datastore/featuretypes.json

#### Response

**Status code:** `200 OK`

	{
	    "featureTypes": [
	        {
	            "name": "my_first_featuretype",
	            "href": "http://hostname/workspaces/my_workspace/datastores/my_datastore/featuretypes/my_first_featuretype.json"
	        },
	        {
	            "name": "my_second_featuretype",
	            "href": "http://hostname/workspaces/my_workspace/datastores/my_datastore/featuretypes/my_second_featuretype.json"
	        }
	    ]
	}

### POST workspaces/{ws}/datastores/{ds}/featuretypes

Configures a new feature type in data store. The feature type musts exit.

This operation creates automatically the associated [layer](layers.md#get-layers).

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}/featuretypes{.extension}

#### Available formats

JSON, XML.

#### Example request

**POST** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes.json

**POST Content-type:** `application-json`

**POST data:**

	{
	    "featureType": {
	        "name": "ne_110m_admin_0_countries",
	        }
	    }
	}

#### Response

**Status code:** `201 Created`

**Location:** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json


### GET workspaces/{ws}/datastores/{ds}/featuretypes/{ft}

Returns the feature type.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}/featuretypes/{ft}{.extension}

#### Available formats

JSON, XML.

#### Example request

**GET** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json

#### Response

**Status code:** `200 OK`

	{
	    "featureType": {
	        "nativeBoundingBox": {
	            "minx": -180,
	            "miny": -90,
	            "maxx": 180,
	            "maxy": 83.64513,
	            "crs": "EPSG:4326"
	        },
	        "nativeCRS": "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9108\"]],AUTHORITY[\"EPSG\",\"4326\"]]",
	        "latLonBoundingBox": {
	            "minx": -180,
	            "miny": -90,
	            "maxx": 180,
	            "maxy": 83.64513,
	            "crs": "EPSG:4326"
	        },
	        "abstract": null,
	        "nativeName": "ne_110m_admin_0_countries",
	        "name": "ne_110m_admin_0_countries",
	        "title": "ne_110m_admin_0_countries",
	        "enabled": true,
	        "projectionPolicy": "NONE",
	        "attributes": [
	            {
	                "length": 4,
	                "type": "Integer",
	                "name": "scalerank"
	            },
	            {
	                "length": 30,
	                "type": "String",
	                "name": "featurecla"
	            },
	            {
	                "length": 16,
	                "type": "Real",
	                "name": "labelrank"
	            },
	            // ...
	           	{
	                "maxOccurs": 1,
	                "type": "polygon",
	                "name": "geometry",
	                "minOccurs": 0
	            }
	        ],
	        "store": {
	            "href": "http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries.json",
	            "name": "ne_110m_admin_0_countries"
	        }
	    }
	}

### DELETE workspaces/{ws}/datastores/{ds}/featuretypes/{ft}

Removes the configuration of the feature type.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}/featuretypes/{ft}{.extension}

#### Available formats

JSON, XML.

#### Example request

**DELETE** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json

#### Response

**Status code:** `200 OK`
