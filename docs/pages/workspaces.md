## Workspaces

A workspace is a grouping of [data stores](datastores.md) and [coverages stores](coveragestores.md).

### GET workspaces

Returns a list containing all workspaces.

#### Resource URL

http://hostname/workspaces{.extension}

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None

#### Example request

**GET http://hostname/workspaces.json**

##### Response

**Status code:** 200 OK

    {
	    "workspaces": [
	        {
	            "href": "http://hostname/workspaces/my_workspace.json",
	            "name": "sample"
	        }
	    ]
	}

### POST workspaces

Creates a new workspace.

#### Resource URL

http://hostname/workspaces{.extension}

#### Available formats

JSON, XML.

#### Parameters

None.

#### Example request

**POST http://hostname/workspaces.json**

**POST Content-type:** `application-json'

**POST data:**

	{
	    "workspace": 
	        {
	            "name": "another_workspace"
	        }
	}

##### Response

**Status code:** 201 OK

**Location:** http://hostname/workspaces/my_workspace.json

### GET workspaces/{ws}

Returns  workspace {ws}.

#### Resource URL

http://hostname/workspaces/{ws}.{extension}

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None

#### Example request

**GET http://hostname/workspaces/my_workspace.json**

##### Response

**Status code:** 200 OK

    {
        "workspace": {
            "name": "my_workspace",
            "dataStores": {
                "href": "http://hostname/workspaces/my_workspace/datastores.json"
            },
            "coverageStores": {
                "href": "http://hostname/workspaces/my_workspace/coveragestores.json"
            }
        }
    }
