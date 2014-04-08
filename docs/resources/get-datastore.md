### GET workspaces/\<ws\>/datastores/\<ds\>

Returns data store \<ds\>.

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>/datastores/\<ds\>\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Example requests

##### Data store is a Shapefile connection

###### XML

`GET http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries.xml`

Returns,

```xml
<dataStore>
    <name>ne_110m_admin_0_countries</name>
    <enabled>True</enabled>
    <workspace>
        <name>my_workspace</name>
        <atom:link href="http://127.0.0.1/workspaces/my_workspace.xml" rel="alternate" type="application/xml"/>
    </workspace>
    <connectionParameters>
        <entry key="url">file:ne_110m_admin_0_countries.shp</entry>
    </connectionParameters>
    <featureTypes>
        <atom:link href="http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes.xml" rel="alternate" type="application/xml"/>
    </featureTypes>
</dataStore>
```

##### Data store is a PostGIS connection

###### XML

`GET http://127.0.0.1/workspaces/my_workspace/datastores/pg_sample.xml`

Returns,

```xml
<dataStore>
    <name>pg_sample</name>
    <enabled>True</enabled>
    <workspace>
        <name>my_workspace</name>
        <atom:link href="http://127.0.0.1/workspaces/my_workspace.xml" rel="alternate" type="application/xml"/>
    </workspace>
    <connectionParameters>
        <entry key="dbtype">postgis</entry>
        <entry key="host">127.0.0.1</entry>
        <entry key="port">5432</entry>
        <entry key="database">my_dbname</entry>
        <entry key="user">postgres</entry>
        <entry key="password">postgres</entry>
    </connectionParameters>
    <featureTypes>
        <atom:link href="http://127.0.0.1/workspaces/my_workspace/datastores/pg_sample/featuretypes.xml" rel="alternate" type="application/xml"/>
    </featureTypes>
</dataStore>
```

#### Compatibility with GeoServer REST API

The XML response is fully compatible with GeoServer REST API.

But the JSON response is not.