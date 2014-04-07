### GET workspaces/_ws_/datastores/_ds_/featuretypes/_ft_

Returns the feature type `_ft_'.

#### Resource URL

http://_hostname_/workspaces/_ws_/datastores/_ds_/featuretypes/_ft.format_

#### Available formats

JSON, XML.

#### Example request

**GET** http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.json

#### Response

**Status code:** `200 OK`

```json
{
    "featureType": {
        "nativeBoundingBox": {
            "minx": -180,
            "miny": -90,
            "maxx": 180,
            "maxy": 83.64513,
            "crs": "EPSG:4326"
        },
        "nativeCRS": "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9108\"]],AUTHORITY[\"EPSG\",\"4326\"]]",
        "latLonBoundingBox": {
            "minx": -180,
            "miny": -90,
            "maxx": 180,
            "maxy": 83.64513,
            "crs": "EPSG:4326"
        },
        "abstract": null,
        "nativeName": "ne_110m_admin_0_countries",
        "name": "ne_110m_admin_0_countries",
        "title": "ne_110m_admin_0_countries",
        "enabled": true,
        "projectionPolicy": "NONE",
        "attributes": [
            {
                "length": 4,
                "type": "Integer",
                "name": "scalerank"
            },
            {
                "length": 30,
                "type": "String",
                "name": "featurecla"
            },
            {
                "length": 16,
                "type": "Real",
                "name": "labelrank"
            },
            // ...
           	{
                "maxOccurs": 1,
                "type": "polygon",
                "name": "geometry",
                "minOccurs": 0
            }
        ],
        "store": {
            "href": "http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries.json",
            "name": "ne_110m_admin_0_countries"
        }
    }
}
```