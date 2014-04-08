### POST layers

Creates a new layers.

#### Resource URL

http://\<hostname\>/layers\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Exemple requests

###### JSON

`POST http://127.0.0.1/layers.json`

Content-type: `application/json`

Data:

```json
{
    "layer": {
        "name": "ne_110m_admin_0_countries",
        "resource": {
            "href": "http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json"}
    }
}
```

Returns,

Status code: `201 Created`

Location: `http://127.0.0.1/layer/ne_110m_admin_0_countries.json

#### Compatibility with GeoServer REST API

`TODO`