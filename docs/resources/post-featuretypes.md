### POST workspaces/\<ws\>/datastores/\<ds\>/featuretypes

Configures a new feature type in data store \<ds\>.
The feature type musts exit.

This operation creates automatically the associated [layer](../mra-reference.md#layers).

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>/datastores/\<ds\>/featuretypes\<.format\>

#### Available formats

JSON, XML.

#### Parameters

None.

#### Example requests

`POST http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes.json`

Content-type: `application/json`

Data:

```json
{
    "featureType": {
        "name": "ne_110m_admin_0_countries",
        }
    }
}
```

Returns,

Status code: `201 Created`

Location: `http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json`

#### Compatibility with GeoServer REST API

`TODO`