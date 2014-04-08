### GET workspaces/\<ws\>/datastores

Returns a list containing data stores in workspace \<ws\>.

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>/datastores\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Exemple requests

###### XML

`GET http://127.0.0.1/workspaces/my_workspace/datastores.xml`

Returns,

```xml
<dataStores>
    <dataStore>
        <name>ne_110m_admin_0_countries</name>
        <atom:link href="http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries.xml" rel="alternate" type="application/xml"/>
    </dataStore>
    <dataStore>
        <name>my_second_datastore</name>
        <atom:link href="http://127.0.0.1/workspaces/my_workspace/datastores/my_second_datastore.xml" rel="alternate" type="application/xml"/>
    </dataStore>
</dataStores>
```

###### JSON

`GET http://127.0.0.1/workspaces/my_workspace/datastores.json`

Returns,

```json
{
    "dataStores": [
        {
            "href": "http://hostname/workspaces/my_workspace/datastores/my_first_datastore.json",
            "name": "my_fisrt_datastore"
        }
        {
            "href": "http://hostname/workspaces/my_workspace/datastores/my_second_datastore.json",
            "name": "my_second_datastore"
        }
    ]
}
```

#### Compatibility with GeoServer REST API

The XML response is fully compatible with GeoServer REST API.

But the JSON response is not. It should be like below.

```json
{
    "dataStores": {
        "dataStore": [
            {
                "href": "http://hostname/workspaces/my_workspace/datastores/my_first_datastore.json",
                "name": "my_fisrt_datastore"
            }
            {
                "href": "http://hostname/workspaces/my_workspace/datastores/my_second_datastore.json",
                "name": "my_second_datastore"
            }
        ]
    }
}
```