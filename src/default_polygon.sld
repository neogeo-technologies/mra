<StyledLayerDescriptor version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
    <NamedLayer>
        <Name>foo</Name>
        <UserStyle>
            <FeatureTypeStyle>
                <Rule>
                    <Name>Class given in default</Name>
                    <PolygonSymbolizer>
                        <Fill>
                            <CssParameter name="fill">#95F9D6</CssParameter>
                        </Fill>
                        <Stroke>
                            <CssParameter name="stroke">#2AAB7E</CssParameter>
                            <CssParameter name="stroke-width">1</CssParameter>
                        </Stroke>
                    </PolygonSymbolizer>
                </Rule>
            </FeatureTypeStyle>
        </UserStyle>
    </NamedLayer>
</StyledLayerDescriptor>