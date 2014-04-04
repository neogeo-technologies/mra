## Layers

A layer is a data resource that could be published by a OGC Web Service. So a layer is the combination of data (feature type or coverage) plus styling (in case of OGC:WMS).

### GET layers

Returns a list of all existing layers.

#### Resource URL

http://hostname/layers{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**GET** http://hostname/layers.json

#### Response

**Status code:** `200 OK`

	{
	    "layers": [
	        {
	            "name": "ne_110m_admin_0_countries",
	            "href": "http://hostname/layers/ne_110m_admin_0_countries.json"
	        }
	    ]
	}


### POST layers

Creates a new layers.

#### Resource URL

http://hostname/layers{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**POST** http://hostname/layers.json

**POST Content-type:** `application-json`

**POST data:**

	{
	    "layer": {
	        "name": "ne_110m_admin_0_countries",
	        "resource": {
	            "href": "http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json"}
	    }
	}

#### Response

**Status code:** `201 Created`

**Location:** http://hostname/layer/just_countries.json


### GET layers/{l}

Returns the layer {l}.

#### Resource URL

http://hostname/layers/{l}{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**GET** http://hostname/layers/ne_110m_admin_0_countries.json

#### Response

**Status code:** `200 OK`

	{
	    "layer": {
	        "name": "ne_110m_admin_0_countries",
	        "resource": {
	            "name": "ne_110m_admin_0_countries",
	            "href": "http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json"
	        },
	        "type": "POLYGON",
	        "enabled": true
	    },
	    "defaultStyle": {
	        "href": "http://hostname/styles/default_polygon.json",
	        "name": "default_polygon"
	    }
	}


### PUT layers/{l}

Modifies the configuration of the layer {l}.

#### Resource URL

http://hostname/layers/{l}{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**PUT** http://hostname/layers/ne_110m_admin_0_countries.json

**POST Content-type:** `application-json`

**POST data:**

	{
	    "layer": {
	        "title": "Countries",
	        "abstract" : "Countries distinguish between metropolitan and independent and semi-independent portions of sovereign states."
	    }
	}

#### Response

**Status code:** `200 OK`


### DELETE layers/{l}

Deletes the layer {l}.

#### Resource URL

http://hostname/layers/{l}{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**DELETE** http://hostname/layers/ne_110m_admin_0_countries.json

#### Response

**Status code:** `200 OK`
