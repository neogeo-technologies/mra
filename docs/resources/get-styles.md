### GET styles

Returns a list containing all available styles.

#### Resource URL

http://\<hostname\>/styles\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Exemple requests

###### XML

`GET http://127.0.0.1/styles.xml`

Returns,

```xml
<styles>
    <style>
        <name>default_point</name>
        <atom:link href="http://127.0.0.1/styles/default_point.xml" rel="alternate" type="application/xml" />
    </style>
    <style>
        <name>default_line</name>
        <atom:link href="http://127.0.0.1/styles/default_line.xml" rel="alternate" type="application/xml" />
    </style>
    <style>
        <name>default_polygon</name>
        <atom:link href="http://127.0.0.1/styles/default_polygon.xml" rel="alternate" type="application/xml" />
    </style>
</styles>
```

#### Compatibility with GeoServer REST API

`TODO`
