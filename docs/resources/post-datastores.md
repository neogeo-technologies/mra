### POST workspaces/_ws_/datastores

Creates a new data store in workspace `_ws_'. 

#### Resource URL

http://_hostname_/workspaces/_ws_/datastores/_ds.format_

#### Available formats

JSON, XML.

#### Example request

**POST** http://hostname/workspaces/my_workspace/datastores.json

**POST Content-type:** `application-json`

**POST data:**

```json
{
    "dataStore": {
        "name": "pg_sample",
        "enabled": true,
        "connectionParameters": {
            "host": "127.0.0.1",
            "user": "postgres",
            "database": "dbname",
            "dbtype": "postgis",
            "password": "postgres",
            "port": "5432"
        }
    }
}
```

#### Response

**Status code:** `201 Created`

**Location:** `http://hostname/workspaces/my_workspace/datastores/pg_sample.json`
