### PUT workspaces/\<ws\>/datastores/\<ds\>

Modifies data store \<ds\>.

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>/datastores/\<ds\>\<.format\>

#### Available formats

JSON, XML.

#### Parameters

None.

#### Example request

##### Data store is a PostGIS connection

###### JSON

`PUT http://127.0.0.1/workspaces/my_workspace/datastores/pg_sample.json`

Content-type: `application/json`

Data:

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
            "user": "mra",
            "password": "foo"
        },
    }
}
```

#### Compatibility with GeoServer REST API

`TODO`