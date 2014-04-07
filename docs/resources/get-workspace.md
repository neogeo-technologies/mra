### GET workspaces/_ws_

Returns workspace `_ws_'.

#### Resource URL

http://_hostname_/workspaces/_ws.format_

#### Available formats

HTML (default value), JSON, XML.

#### Example request

**GET** http://hostname/workspaces/my_workspace.json

##### Response

**Status code:** `200 OK`

```json
{
    "workspace": {
        "name": "my_workspace",
        "dataStores": {
            "href": "http://hostname/workspaces/my_workspace/datastores.json"
        },
        "coverageStores": {
            "href": "http://hostname/workspaces/my_workspace/coveragestores.json"
        }
    }
}
```