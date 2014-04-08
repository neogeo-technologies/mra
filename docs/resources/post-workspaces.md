### POST workspaces

Creates a new workspace.

#### Resource URL

http://\<hostname\>/workspaces\<.format\>

#### Available formats

JSON, XML.

#### Parameters

None.

#### Example requests

###### JSON

`POST http://127.0.0.1/workspaces.json`

Content-type: `application/json`

Data:

```json
{
    "workspace": 
        {
            "name": "another_workspace"
        }
}
```

###### XML

`POST http://127.0.0.1/workspaces.xml`

Content-type: `application/xml`

Data:

```xml
<workspace>
	<name>another_workspace</name>
</workspace>
```

Returns,

Status code: `201 Created`

With Location: `http://hostname/workspaces/another_workspace.xml`

#### Compatibility with GeoServer REST API

Fully compatible.