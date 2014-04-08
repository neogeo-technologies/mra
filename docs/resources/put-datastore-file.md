### PUT workspaces/\<ws\>/datastores/\<ds\>/file\<.extension\>

Uploads a file from a local source and creates the data store \<ds\>.
Files must be zipped.

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>/datastores/\<ds\>/file\<.extension\>

#### Available extensions

SHP (ShapeFile).

#### Parameters

None.

#### Example request

`PUT http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/file.shp`

Content-type: `application/zip`

Data: `binary-data`

Returns

Status code: `200 OK`

#### Compatibility with GeoServer REST API

`TODO`