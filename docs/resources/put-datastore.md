### PUT workspaces/_ws_/datastores/_ds_

Modifies data store `_ds_'.

#### Resource URL

http://_hostname_/workspaces/_ws_/datastores/_ds.format_

#### Available formats

JSON, XML.

#### Example request

**PUT http://hostname/workspaces/my_workspace/datastores/pg_sample.json

**PUT Content-type:** `application-json`

**PUT Data:**

```json
{
    "dataStore": {
        "name": "pg_sample",
        "enabled": false,
        "connectionParameters": {
            "dbtype": "postgis",
            "host": "127.0.0.1",
            "port": "5432",
            "database": "my_dbname",
            "user": "mra",
            "password": "foo"
        },
    }
}
```

#### Response

**Status code:** `201 Created`

**Location:** `http://hostname/workspaces/my_workspace/datastores/pg_sample.json`
