### GET layers

Returns a list of all existing layers.

#### Resource URL

http://\<hostname\>/layers\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Exemple requests

###### XML

`GET http://127.0.0.1/layers.xml`

Results,

```xml
<layers>
	<layer>
		<name>ne_110m_admin_0_countries</name>
		<atom:link href="http://127.0.0.1/layers/ne_110m_admin_0_countries.json" rel="alternate" type="application/xml"/>
	</layer>
</layers>
```

###### JSON

`GET http://127.0.0.1/layers.json`

Results,

```json
{
    "layers": [
        {
            "name": "ne_110m_admin_0_countries",
            "href": "http://127.0.0.1/layers/ne_110m_admin_0_countries.json"
        }
    ]
}
```

#### Compatibility with GeoServer REST API

The XML response is fully compatible with GeoServer REST API.

But the JSON response is not.