### GET workspaces

Returns a list containing all workspaces.

#### Resource URL

http://\<hostname\>/workspaces\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Example requests

###### XML

`GET http://127.0.0.1/workspaces.xml`

Returns,

```xml
<workspaces>
    <workspace>
        <name>my_workspace</name>
        <atom:link href="http://127.0.0.1/workspaces/my_workspace.xml" rel="alternate" type="application/xml"/>
    </workspace>
</workspaces>
```

###### JSON

`GET http://127.0.0.1/workspaces.json`

Returns,

```json
{
    "workspaces": [
        {
            "name": "my_workspace",
            "href": "http://127.0.0.1/workspaces/my_workspace.json"
        }
    ]
}
```

#### Compatibility with GeoServer REST API

The XML response is fully compatible with GeoServer REST API.

But the JSON response is not. 
It should be like above.

```json
{
    "workspaces": {
        "workspace": [
            {
                "name": "my_workspace",
                "href": "http://127.0.0.1/workspaces/my_workspace.json"
            }
        ]
    }
}
```