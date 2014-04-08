### PUT layergroups/\<lg\>

Modifies layer group \<lg\> i.e. adding or removing layers of the group.

#### Resource URL

http://\<hostname\>/layergroups/\<lg\>\<.format\>

#### Available formats

JSON, XML.

#### Parameters

None.

#### Exemple requests

###### JSON

`PUT http://127.0.0.1/layergroups/ne_basemap.xml`

Content-type: `application/xml`

Data:

```xml
<layerGroup>
  <name>ne_basemap</name>
  <layers>
	<layer>countries</layer>
	<layer>rivers</layer>
    <layer>populated_places</layer>
  </layers>
</layerGroup>
```

#### Compatibility with GeoServer REST API

`TODO`