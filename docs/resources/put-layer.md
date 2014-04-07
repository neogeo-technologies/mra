### PUT layers/_l_

Modifies the configuration of the layer `_l_'.

#### Resource URL

http://_hostname_/layers/_l.format_

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**PUT** http://hostname/layers/ne_110m_admin_0_countries.json

**PUT Content-type:** `application-json`

**PUT data:**

```json
{
    "layer": {
        "title": "Countries",
        "abstract" : "Countries distinguish between metropolitan and independent and semi-independent portions of sovereign states."
    }
}
```

#### Response

**Status code:** `200 OK`
