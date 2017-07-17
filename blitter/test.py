import json
import xmltodict # Imported from https://github.com/martinblech/xmltodict
import xml.etree.ElementTree as ET
from xml.dom import minidom

import jpylyzer.jpylyzer as jpylyzer # Imported from https://github.com/britishlibrary/jpylyzer
import genblit


if __name__ == '__main__':
    jpylyzer_xml = jpylyzer.checkOneFile('../jython/src/test/resources/test-data/vdc_100022551931.0x000001')
    
    blit_xml = genblit.to_blit(jpylyzer_xml)
    
    xmlOut = ET.tostring(blit_xml, 'UTF-8', 'xml')
    xmlPretty = minidom.parseString(xmlOut).toprettyxml('    ')
    
    print(xmlPretty)

    xmlDict = xmltodict.parse(xmlOut)
    xmlJson = json.dumps(xmlDict, indent=True)
    
    print(xmlJson)
    
    with open("blit.xml", "w") as f:
        f.write(xmlPretty)
    
