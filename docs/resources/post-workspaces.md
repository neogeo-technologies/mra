### POST workspaces

Creates a new workspace.

#### Resource URL

http://_hostname_/workspaces_.format_

#### Available formats

JSON, XML.

#### Example request

**POST** http://hostname/workspaces.json

**POST Content-type:** `application-json`

**POST data:**

```json
{
    "workspace": 
        {
            "name": "another_workspace"
        }
}
```

##### Response

**Status code:** `201 OK`

**Location:** `http://hostname/workspaces/my_workspace.json`