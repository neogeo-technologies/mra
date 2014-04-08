### GET layers/\<l\>

Returns the layer \<l\>.

#### Resource URL

http://\<hostname\>/layers/\<l\>\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Exemple requests

###### XML

`GET http://127.0.0.1/layers/ne_110m_admin_0_countries.xml`

Returns,

```xml
<layer>
    <enabled>True</enabled>
    <name>ne_110m_admin_0_countries</name>
    <title>ne_110m_admin_0_countries</title>
    <abstract>ne_110m_admin_0_countries</abstract>
    <type>POLYGON</type>
    <defaultStyle>
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="http://127.0.0.1/styles/default_polygon.xml" rel="alternate" type="application/xml" />
        <name>default_polygon</name>
    </defaultStyle>        
    <resource>
        <name>ne_110m_admin_0_countries</name>
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.xml" rel="alternate" type="application/xml" />
    </resource>
</layer>
```

###### JSON

`GET http://127.0.0.1/layers/ne_110m_admin_0_countries.json`

Returns,

```json
{
    "layer": {
        "enabled": true,
        "name": "ne_110m_admin_0_countries",
        "type": "POLYGON",
        "defaultStyle": {
            "name": "default_polygon",
            "href": "http://127.0.0.1/styles/default_polygon.json"
        },
        "resource": {
            "name": "ne_110m_admin_0_countries",
            "href": "http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json"
        }
    }
}
```

#### Compatibility with GeoServer REST API

`TODO`
