package uk.bl.image.blitter;

import org.python.core.PyString;
import org.python.util.PythonInterpreter;

/**
 * 
 * @author user
 * 
 */
public class GenerateBLIT {

    protected String[] args;

	public GenerateBLIT(String[] args) {
        this.args = args;
	}

    public static void main(String[] args) {
		System.out.println("Java started");

        PythonInterpreter interp = new PythonInterpreter();

        //
        interp.exec("from jpylyzer import jpylyzer");
        interp.exec("import genblit");
        interp.exec(
                "jxml = jpylyzer.checkOneFile('src/test/resources/test-data/vdc_100022551931.0x000001')");
        interp.exec("bxml = genblit.to_blit(jxml)");

        //
        interp.exec("import xml.etree.ElementTree as ET");
        interp.exec("from xml.dom import minidom");
        PyString xmlString = (PyString) interp
                .eval("minidom.parseString(ET.tostring(bxml, 'UTF-8', 'xml')).toprettyxml('    ')");

        //
        System.out.println("" + xmlString);

        interp.close();
		System.out.println("Java exiting");
	}

}
