### PUT fonts

Uploads fonts from a local source.
Files must be zipped.

#### Resource URL

http://\<hostname\>/fonts\<.format\>

#### Available formats

TTF (TrueType).

#### Parameters

None.

#### Exemple requests

###### 

`PUT http://127.0.0.1/fonts.tff`

Content-type: `application/zip`

Data: `binary-data`

Returns

Status code: `200 OK`

#### Compatibility with GeoServer REST API

`TODO`