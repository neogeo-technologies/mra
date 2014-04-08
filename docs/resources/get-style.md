### GET styles/\<s\>

Returns style \<s\>.

#### Resource URL

http://\<hostname\>/styles/\<s\>\<.format\>

#### Available formats

HTML (default value), JSON, XML, [SLD](http://www.opengeospatial.org/standards/sld).

#### Parameters

None.

#### Exemple requests

###### XML

`GET http://127.0.0.1/styles/countries_style.xml`

Returns,

```xml
<style>
    <name>countries_style</name>
    <filename>countries_style.sld</filename>
    <sldVersion>
        <version>1.0.0</version>
    </sldVersion>
</style>
```

###### SLD

`GET http://127.0.0.1/styles/countries_style.sld`

Returns,

```xml
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" 
                       xmlns:ogc="http://www.opengis.net/ogc" 
                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1.0" 
                       xmlns:xlink="http://www.w3.org/1999/xlink" 
                       xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" 
                       xmlns:se="http://www.opengis.net/se">
  <NamedLayer>
    <se:Name>countries_style</se:Name>
    <UserStyle>
      <se:Name>countries_style</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Name>Single symbol</se:Name>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#fff5e0</se:SvgParameter>
            </se:Fill>
            <se:Stroke>
              <se:SvgParameter name="stroke">#4b4044</se:SvgParameter>
              <se:SvgParameter name="stroke-width">0.4</se:SvgParameter>
            </se:Stroke>
          </se:PolygonSymbolizer>
        </se:Rule>
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
```

#### Compatibility with GeoServer REST API

`TODO`
