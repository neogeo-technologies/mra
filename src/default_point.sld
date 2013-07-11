<StyledLayerDescriptor version="1.0.0" xmlns:xsi="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
  <NamedLayer>
    <Name>foo</Name>
    <UserStyle>
      <FeatureTypeStyle>
	<Rule>
	  <Name>Class given in default</Name>
	  <PointSymbolizer>
	    <Graphic>
	      <Size>6.0</Size>
	      <Mark>
		<WellKnownName>circle</WellKnownName>
		<Fill>
		  <CssParameter name="fill">#6D35AD</CssParameter>
		</Fill>
	      </Mark>
	    </Graphic>
	  </PointSymbolizer>
	</Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>