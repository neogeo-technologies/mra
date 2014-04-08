### GET workspaces/\<ws\>

Returns workspace \<ws\>.

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Example requests

###### JSON

`GET http://127.0.0.1/workspaces/my_workspace.json`

Returns

Status code: `200 OK`

```json
{
    "workspace": {
        "name": "my_workspace",
        "dataStores": {
            "href": "http://127.0.0.1/workspaces/my_workspace/datastores.json"
        },
        "coverageStores": {
            "href": "http://127.0.0.1/workspaces/my_workspace/coveragestores.json"
        }
    }
}
```

###### XML

`GET http://127.0.0.1/workspaces/my_workspace.xml`

Returns,

Status code: `200 OK`

```xml
<workspace>
	<name>my_workspace</name>
	<dataStores>
		<atom:link href="http://127.0.0.1/workspaces/my_workspace/datastores.xml" rel="alternate" type="application/xml"/>
	</dataStores>
	<coverageStores>
		<atom:link href="http://127.0.0.1/workspaces/my_workspace/coveragestores.xml" rel="alternate" type="application/xml"/>
	</coverageStores>
</workspace>
```

#### Compatibility with GeoServer REST API

The XML response is fully compatible with GeoServer REST API.

But the JSON response is not. 
It should be like below.

```json
{
    "workspace": {
        "name": "my_workspace",
        "dataStores": "http://127.0.0.1/workspaces/my_workspace/datastores.json",
        "coverageStores": "http://127.0.0.1/workspaces/my_workspace/coveragestores.json"
    }
}
```