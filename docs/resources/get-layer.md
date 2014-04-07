### GET layers/_l_

Returns the layer `_l_'.

#### Resource URL

http://_hostname_/layers/_l.format_

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**GET** http://hostname/layers/ne_110m_admin_0_countries.json

#### Response

**Status code:** `200 OK`

```json
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
```