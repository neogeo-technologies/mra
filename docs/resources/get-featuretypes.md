### GET workspaces/_ws_/datastores/_ds_/featuretypes

Returns all feature type in data store `_ds_'.

#### Resource URL

http://_hostname_/workspaces/_ws_/datastores/_ds_/featuretypes_.format_

#### Available formats

HTML (default value), JSON, XML.

#### Example request

**GET** http://hostname/workspaces/my_workspace/datastores/my_datastore/featuretypes.json

#### Response

**Status code:** `200 OK`

```json
{
    "featureTypes": [
        {
            "name": "my_first_featuretype",
            "href": "http://hostname/workspaces/my_workspace/datastores/my_datastore/featuretypes/my_first_featuretype.json"
        },
        {
            "name": "my_second_featuretype",
            "href": "http://hostname/workspaces/my_workspace/datastores/my_datastore/featuretypes/my_second_featuretype.json"
        }
    ]
}
```