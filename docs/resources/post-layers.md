### POST layers

Creates a new layers.

#### Resource URL

http://_hostname_/layers_.format_

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**POST** http://hostname/layers.json

**POST Content-type:** `application-json`

**POST data:**

```json
{
    "layer": {
        "name": "ne_110m_admin_0_countries",
        "resource": {
            "href": "http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json"}
    }
}
```

#### Response

**Status code:** `201 Created`

**Location:** http://hostname/layer/just_countries.json
