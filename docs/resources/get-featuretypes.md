### GET workspaces/\<ws\>/datastores/\<ds\>/featuretypes

Returns all feature type in data store \<ds\>.

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>/datastores/\<ds\>/featuretypes\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Example requests

###### XML

`GET http://127.0.0.1/workspaces/my_workspace/datastores/my_datastore/featuretypes.xml`

Returns,

```xml
<featureTypes>
    <featureType>
        <name>ne_110m_admin_0_countries</name>
        <atom:link href="http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json" rel="alternate" type="application/xml"/>
    </featureType>
</featureTypes>
```

###### JSON

`GET http://127.0.0.1/workspaces/my_workspace/datastores/my_datastore/featuretypes.json`

Returns,

```json
{
    "featureTypes": [
        {
            "name": "my_first_featuretype",
            "href": "http://127.0.0.1/workspaces/my_workspace/datastores/my_datastore/featuretypes/my_first_featuretype.json"
        },
        {
            "name": "my_second_featuretype",
            "href": "http://127.0.0.1/workspaces/my_workspace/datastores/my_datastore/featuretypes/my_second_featuretype.json"
        }
    ]
}
```

#### Compatibility with GeoServer REST API

The XML response is fully compatible with GeoServer REST API.

But the JSON response is not. It should be like below.

```json
{
    "featureTypes": {
        "featureType": [
            {
                "name": "my_first_featuretype",
                "href": "http://127.0.0.1/workspaces/my_workspace/datastores/my_datastore/featuretypes/my_first_featuretype.json"
            },
            {
                "name": "my_second_featuretype",
                "href": "http://127.0.0.1/workspaces/my_workspace/datastores/my_datastore/featuretypes/my_second_featuretype.json"
            }
        ]
    }
}
```