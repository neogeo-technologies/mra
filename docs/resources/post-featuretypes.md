### POST workspaces/_ws_/datastores/_ds_/featuretypes

Configures a new feature type in data store `_ds_'.
The feature type musts exit.

This operation creates automatically the associated [layer](../mra-reference.md#layers).

#### Resource URL

http://_hostname_/workspaces/_ws_/datastores/_ds_/featuretypes_.format_

#### Available formats

JSON, XML.

#### Example request

**POST** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes.json

**POST Content-type:** `application-json`

**POST data:**

```json
{
    "featureType": {
        "name": "ne_110m_admin_0_countries",
        }
    }
}
```

#### Response

**Status code:** `201 Created`

**Location:** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json
