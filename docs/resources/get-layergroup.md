### GET layergroups/\<lg\>

Returns the layer group \<lg\>.

#### Resource URL

http://\<hostname\>/layergroups/\<lg\>\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Exemple requests

###### XML

`GET http://127.0.0.1/layergroups/ne_basemap.xml`

Returns,

```xml
<layerGroup>
    <name>ne_basemap</name>
    <mode>NAMED</mode>
    <publishables>
        <published>
            <name>countries</name>
            <atom:link href="http://192.168.56.181/mra/layers/countries.xml" rel="alternate" type="application/xml"/>
        </published>
    </publishables>
    <bounds>
        <minx>-180.0</minx>
        <miny>-90.0</miny>
        <maxx>180.0</maxx>
        <maxy>83.64513</maxy>
        <crs>EPSG:4326</crs>
    </bounds>
</layerGroup>
```

#### Compatibility with GeoServer REST API

`TODO`
