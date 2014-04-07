### PUT workspaces/_ws_/datastores/_ds_/file_.extension_

Uploads a file from a local source and creates the data store `_ds_'.
File must be zipped.

#### Resource URL

http://_hostname_/workspaces/_ws_/datastores/_ds_/file_.extension_

#### Available extensions

SHP (ShapeFile).

#### Parameters

`TODO`

#### Example request

**PUT** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/file.shp

**PUT Content-type:** `application-zip`

**PUT binary-data**

#### Response

**Status code:** `200 OK`
