### POST layergroups

Creates a new layer group.

#### Resource URL

http://\<hostname\>/layergroups\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Exemple requests

###### XML

`POST http://127.0.0.1/layergroups.xml`

Content-type: `application/xml`

Data:

```xml
<layerGroup>
  <name>ne_basemap</name>
  <layers>
    <layer>countries</layer>
    <layer>populated_places</layer>
  </layers>
</layerGroup>
```

Returns,

Status code: `201 Created`

Location: `http://127.0.0.1/layergroups/ne_basemap.xml

#### Compatibility with GeoServer REST API

`TODO`