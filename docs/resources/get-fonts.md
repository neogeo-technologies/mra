### GET fonts

Returns the list of available fonts.

#### Resource URL

http://\<hostname\>/fonts\<.format\>

#### Available formats

HTML (default value), JSON, XML.

#### Parameters

None.

#### Exemple requests

###### XML

`GET http://127.0.0.1/fonts.xml`

Returns,

```xml
<fonts>
    <font>DejaVuSansCondensed</font>
    <font>DejaVuSans-BoldOblique</font>
    <font>DejaVuSerifCondensed</font>
    <font>DejaVuSansMono-Oblique</font>
    <font>DejaVuSerifCondensed-BoldItalic</font>
    <font>DejaVuSerifCondensed-Bold</font>
    <font>DejaVuSans-Bold</font>
    <font>DejaVuSans-Oblique</font>
    <font>DejaVuSerifCondensed-Italic</font>
    <font>DejaVuSansMono-BoldOblique</font>
    <font>DejaVuSans</font>
    <font>DejaVuSansMono-Bold</font>
    <font>DejaVuSansCondensed-Bold</font>
    <font>DejaVuSansMono</font>
    <font>DejaVuSerif-Bold</font>
    <font>DejaVuSansCondensed-Oblique</font>
    <font>DejaVuSans-ExtraLight</font>
    <font>DejaVuSansCondensed-BoldOblique</font>
    <font>DejaVuSerif-Italic</font>
    <font>DejaVuSerif-BoldItalic</font>
    <font>DejaVuSerif</font>
</fonts>
```

#### Compatibility with GeoServer REST API

`TODO`