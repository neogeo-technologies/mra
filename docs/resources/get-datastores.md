### GET workspaces/_ws_/datastores

Returns a list containing data stores in workspace `_ws_'.

#### Resource URL

http://_hostname_/workspaces/_ws_/datastores_.format_

#### Available formats

HTML (default value), JSON, XML.

#### Exemple request

**GET** http://hostname/workspaces/my_workspace/datastores.json

#### Response

**Status code:** `200 OK`

```json
{
    "dataStores": [
        {
            "href": "http://hostname/workspaces/my_workspace/datastores/my_fisrt_datastore.json",
            "name": "my_fisrt_datastore"
        }
        {
            "href": "http://hostname/workspaces/my_workspace/datastores/my_second_datastore.json",
            "name": "my_second_datastore"
        }
    ]
}
```