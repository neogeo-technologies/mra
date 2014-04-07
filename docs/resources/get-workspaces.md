### GET workspaces

Returns a list containing all workspaces.

#### Resource URL

http://_hostname_/workspaces_.format_

#### Available formats

HTML (default value), JSON, XML.

#### Example request

**GET** http://hostname/workspaces.json

##### Response

**Status code:** `200 OK`

```json
{
    "workspaces": [
        {
            "href": "http://hostname/workspaces/my_workspace.json",
            "name": "sample"
        }
    ]
}
```