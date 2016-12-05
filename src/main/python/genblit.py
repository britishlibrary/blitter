import xml.etree.ElementTree as ET



def to_blit(jpylyzer_xml):
    '''
    Generates 'blit' xml from jpylyzer output.
    
    ----
    
    B.4 Tile-component division into resolutions and sub-bands
    
    Each image component is wavelet transformed with N_L decomposition levels as explained in Annex F. As a result, the
    component is available at N_L + 1 distinct resolutions, denoted r = 0,1,...,N_L. The lowest resolution, r = 0, is represented by
    the N_L LL band. In general, resolution r is obtained by discarding sub-bands nHH, nHL, nLH for 
    n = 1 through N_L-r and reconstructing the image component from the remaining sub-bands.
    '''
    '''
    Note the number of 'levels' corresponds to the number of times the DWT is applied.
    This means there are levels+1 resolutions, with the lowest corresponding to the reduced original.
    
    Thus, when there are 6 levels, 7  precinct dimensions are found, starting with the smallest (thumbnail), up to the largest.
    
    Hence, the first (zeroth) resolution does not correspond to a dwt_level. The second (r=1) resolution corresponds to the 
    last (N_L - 1) level.
    '''
    
    prop = jpylyzer_xml.find('properties')
    
    ET.register_namespace('blit',"http://bl.uk/namespaces/blit")
    
    root = ET.Element('blit:blimagetech', 
                      { "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", 
                       "xmlns:xsd": "http://www.w3.org/2001/XMLSchema", 
                       "schemaLocation": "http://bl.uk/namespaces/blit ./blit_v02.xsd",
                       "xmlns:blit" : "http://bl.uk/namespaces/blit" } )
    
    image = ET.SubElement(root, "image")
    image.set("offset", "0")
    
    dim = ET.SubElement(image, "blit:dimension")
    
    dimw = ET.SubElement(dim, "blit:width")
    dimw.set("unit", "pixel")
    dimw.text = prop.find('jp2HeaderBox/imageHeaderBox/width').text    
    dimh = ET.SubElement(dim, "blit:height")
    dimh.set("unit", "pixel")
    dimh.text = prop.find('jp2HeaderBox/imageHeaderBox/height').text
    
    res = ET.SubElement(image, "blit:resolution")
    resv = ET.SubElement(res, "blit:x")
    resv.set("unit", "ppi")
    resv.text = str(int(float(prop.find('jp2HeaderBox/resolutionBox/captureResolutionBox/hRescInPixelsPerInch').text)))
    resh = ET.SubElement(res, "blit:y")
    resh.set("unit", "ppi")
    resh.text = str(int(float(prop.find('jp2HeaderBox/resolutionBox/captureResolutionBox/vRescInPixelsPerInch').text)))
    
    chan = ET.SubElement(image, "blit:channels")
    chan.text = prop.find('jp2HeaderBox/imageHeaderBox/nC').text

    chan = ET.SubElement(image, "blit:bitsperchannel")
    chan.text = prop.find('jp2HeaderBox/imageHeaderBox/bPCDepth').text

    # Format section:    
    fmt = ET.SubElement(image, "blit:format")
    fmt.set("xsi:type","blit:jpeg2000")
    
    jp2_compression = ET.SubElement(fmt, "blit:jp2_compression")
    if "irreversible" in prop.find('contiguousCodestreamBox/cod/transformation').text:
        jp2_compression.set("type","JPEG2000_Lossy")
    else: 
        jp2_compression.set("type","JPEG2000_Lossless")
    
    jp2_codeblocksize = ET.SubElement(fmt, "blit:jp2_codeblocksize")
    jp2_cbx = ET.SubElement(jp2_codeblocksize,"blit:jp2_cbx")
    jp2_cbx.text = prop.find('contiguousCodestreamBox/cod/codeBlockWidth').text
    jp2_cby = ET.SubElement(jp2_codeblocksize,"blit:jp2_cby")
    jp2_cby.text = prop.find('contiguousCodestreamBox/cod/codeBlockHeight').text
    
    jp2_layers = ET.SubElement(fmt, "blit:jp2_layers")
    jp2_layers.text = prop.find('contiguousCodestreamBox/cod/layers').text
    
    jp2_progressionorder = ET.SubElement(fmt, "blit:jp2_progressionorder")
    jp2_progressionorder.text = prop.find('contiguousCodestreamBox/cod/order').text
        
    jp2_levels = ET.SubElement(fmt, "blit:jp2_levels")
    jp2_levels.text = prop.find('contiguousCodestreamBox/cod/levels').text
        
    jp2_tile_dimensions = ET.SubElement(fmt, "blit:jp2_tile_dimensions")
    jp2_tile = ET.SubElement(jp2_tile_dimensions, "blit:jp2_tile")
    jp2_tile.set("dwt_level", ",".join(str(x) for x in range(1,int(jp2_levels.text) + 1)))
    jp2_tile_x = ET.SubElement(jp2_tile,"blit:jp2_tile_x")
    jp2_tile_x.text = prop.find('contiguousCodestreamBox/siz/xTsiz').text
    jp2_tile_y = ET.SubElement(jp2_tile,"blit:jp2_tile_y")
    jp2_tile_y.text = prop.find('contiguousCodestreamBox/siz/yTsiz').text
    
    # Extract the precincts if present
    if prop.find('contiguousCodestreamBox/cod/precincts').text == "yes":
        jp2_precincts = ET.SubElement(fmt, "blit:jp2_precincts")
        Psx = prop.findall('contiguousCodestreamBox/cod/precinctSizeX')
        Psy = prop.findall('contiguousCodestreamBox/cod/precinctSizeY')
        dwt_levels = ""
        currSize  = Psx[6].text
        for l in range(1,len(Psx) + 1): # 1,2,3,4,5,6,7
            i = len(Psx) - l # 6,5,4,3,2,1,0
            # If this is the last one, or differs from the previous one:
            if i == 0 or currSize != Psx[i].text:
                dwt_levels = dwt_levels[1:]
                jp2_precinct = ET.SubElement(jp2_precincts, "blit:jp2_precinct")
                jp2_precinct.set("dwt_level", dwt_levels)
                jp2_precinct_x = ET.SubElement(jp2_precinct, "blit:jp2_precinct_x")
                jp2_precinct_x.text = currSize
                jp2_precinct_y = ET.SubElement(jp2_precinct, "blit:jp2_precinct_y")
                jp2_precinct_y.text = currSize
                # Store the new current size:
                currSize = Psx[i].text
                # Reset the levels:
                dwt_levels = ""
                    
            # Construct the next levels string:
            dwt_levels += ",%i" % l

    return root

    
    

