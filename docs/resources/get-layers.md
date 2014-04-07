### GET layers

Returns a list of all existing layers.

#### Resource URL

http://_hostname_/layers_.format_

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**GET** http://hostname/layers.json

#### Response

**Status code:** `200 OK`

```json
{
    "layers": [
        {
            "name": "ne_110m_admin_0_countries",
            "href": "http://hostname/layers/ne_110m_admin_0_countries.json"
        }
    ]
}
```