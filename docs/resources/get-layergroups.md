### GET layergroups

Returns a list containing all existing layer groups.

#### Resource URL

http://\<hostname\>/layergroups\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Exemple requests

###### XML

`GET http://127.0.0.1/layergroups.xml`

Results,

```xml
<layerGroups>
    <layerGroup>
        <name>ne_basemap</name>
        <atom:link href="http://192.168.56.181/mra/layergroups/ne_basemap.xml" rel="alternate" type="application/xml"/>
    </layerGroup>
</layerGroups>
```

`GET http://127.0.0.1/layergroups.json`

Results,

```xml
{
    "layerGroups": [
        {
            "name": "ne_basemap",
            "href": "http://192.168.56.181/mra/layergroups/ne_basemap.json"
        }
    ]
}
```

#### Compatibility with GeoServer REST API

`TODO`