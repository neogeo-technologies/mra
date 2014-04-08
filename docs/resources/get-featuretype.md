### GET workspaces/\<ws\>/datastores/\<ds\>/featuretypes/\<ft\>

Returns the feature type \<ft\>.

#### Resource URL

http://\<hostname\>/workspaces/\<ws\>/datastores/\<ds\>/featuretypes/\<ft\>\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Example request

###### XML

`GET http://hostname/workspaces/my_workspace/datastores/ne_110m_admin_0_countries/featuretypes/ne_110m_admin_0_countries.xml`

Returns,

```xml
<featureType>
    <name>ne_110m_admin_0_countries</name>
    <nativeName>ne_110m_admin_0_countries</nativeName>
    <title>ne_110m_admin_0_countries</title>
    <nativeCRS>GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9108"]],AUTHORITY["EPSG","4326"]]</nativeCRS>
    <nativeBoundingBox>
        <minx>-180.0</minx>
        <miny>-90.0</miny>
        <maxx>180.0</maxx>
        <maxy>83.64513</maxy>
        <crs>EPSG:4326</crs>
    </nativeBoundingBox>
    <latLonBoundingBox>
        <minx>-180.0</minx>
        <miny>-90.0</miny>
        <maxx>180.0</maxx>
        <maxy>83.64513</maxy>
        <crs>EPSG:4326</crs>
    </latLonBoundingBox>  
    <projectionPolicy>NONE</projectionPolicy>
    <enabled>True</enabled>
    <store>
        <name>ne_110m_admin_0_countries</name>
        <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="http://127.0.0.1/workspaces/my_workspace/datastores/ne_110m_admin_0_countries.xml" rel="alternate" type="application/xml" />
    </store>
    <attributes>
        <attribute>
            <name>scalerank</name>
            <type>Integer</type>
            <length>4</length>
        </attribute>
        <attribute>
            <name>featurecla</name>
            <type>String</type>
            <length>30</length>
        </attribute>
        <!-- (...) -->
        <attribute>
            <name>geometry</name>
            <type>polygon</type>
            <minOccurs>0</minOccurs>
            <maxOccurs>1</maxOccurs>
        </attribute>
    </attributes>
</featureType>
```

#### Compatibility with GeoServer REST API

`TODO`