### PUT layers/\<l\>

Modifies the configuration of the layer \<l\>.

#### Resource URL

http://\<hostname\>/layers/\<l\>\<.format\>

#### Available formats

JSON, XML.

#### Parameters

None.

#### Exemple requests

###### JSON

`PUT http://127.0.0.1/layers/ne_110m_admin_0_countries.json`

Content-type: `application/json`

Data:

```json
{
    "layer": {
        "title": "Countries",
        "abstract" : "Countries distinguish between metropolitan and independent and semi-independent portions of sovereign states."
    }
}
```

#### Compatibility with GeoServer REST API

`TODO`