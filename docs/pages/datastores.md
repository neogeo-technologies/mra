## DataStores

A data store is a source of spatial data that is vector based.


### GET workspaces/{ws}/datastores

Returns a list containing data stores in workspace.

#### Resource URL

http://hostname/workspaces/{ws}/datastores.{extension}

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None

#### Exemple request

**GET http://hostname/workspaces/my_workspace/datastores.json**

**Status code:** 200 OK

**Response:**

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

http://hostname/workspaces/{ws}/datastores/{ds}.{extension}

#### Available formats

JSON, XML.

#### Parameters

None.

#### Example request

**POST http://hostname/workspaces/my_workspace/datastores.json**

**POST Content-type:** `application-json'

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

**Status code:** 201 OK

**Location:** http://hostname/workspaces/my_workspace/datastores/pg_sample.json


### GET workspaces/{ws}/datastores/{ds}

Returns data store {ds}.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}.{extension}

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None

#### Example request

**GET http://hostname/workspaces/my_workspace/datastores/pg_sample.json

**Status code:** 200 OK

**Response:**

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

http://hostname/workspaces/{ws}/datastores/{ds}.{extension}

#### Available formats

JSON, XML.

#### Parameters

None

#### Example request

**PUT http://hostname/workspaces/my_workspace/datastores/pg_sample.json

**PUT Content-type:** `application-json'

**Response:**

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

**Status code:** 201 OK

**Location:** http://hostname/workspaces/my_workspace/datastores/pg_sample.json


### DELETE workspaces/{ws}/datastores/{ds}

Deletes data store {ds}.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}.{extension}

#### Available formats

JSON, XML.

#### Parameters

None

#### Example request

**DELETE http://hostname/workspaces/my_workspace/datastores/pg_sample.json

**Status code:** 200 OK


### PUT workspaces/{ws}/datastores/{ds}/file.{extension}

Uploads a file from a local source and creates the data store.
File must be zipped.

#### Resource URL

http://hostname/workspaces/{ws}/datastores/{ds}/file.{extension}

#### Available formats

SHP (ShapeFile).

#### Parameters

None

#### Example request

**PUT http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/file.shp

**PUT Content-type:** `application-zip'

**PUT binary-data**

**Status code:** 200
