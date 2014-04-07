### GET workspaces/_ws_/datastores/_ds_

Returns data store `_ds_'.

#### Resource URL

http://_hostname_/workspaces/_ws_/datastores/_ds.format_

#### Available formats

HTML (default value), JSON, XML.

#### Example request

**GET** http://hostname/workspaces/my_workspace/datastores/pg_sample.json

#### Response

**Status code:** `200 OK`

```json
{
    "dataStore": {
        "name": "pg_sample",
        "enabled": true,
        "connectionParameters": {
            "dbtype": "postgis",
            "host": "127.0.0.1",
            "port": "5432",
            "database": "my_dbname",
            "user": "postgres",
            "password": "postgres"
        },
        "featureTypes": {
            "href": "http://hostname/workspaces/my_workspace/datastores/pg_sample/featuretypes.json"
        },
        "workspace": {
            "href": "http://hostname/workspaces/my_workspace.json",
            "name": "my_workspace"
        }
    }
}
```