### POST workspaces/\<ws\>/datastores

Creates a new data store in workspace \<ws\>.

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>/datastores/\<ds\>\<.format\>

#### Available formats

JSON, XML.

#### Parameters

None.

#### Example requests

##### Data store is a PostGIS connection

###### JSON

`POST http://127.0.0.1/workspaces/my_workspace/datastores.json`

Content-type: `application/json`

Data:

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

Returns,

Status code: `201 Created`

Location: `http://127.0.0.1/workspaces/my_workspace/datastores/pg_sample.json`

#### Compatibility with GeoServer REST API

`TODO`