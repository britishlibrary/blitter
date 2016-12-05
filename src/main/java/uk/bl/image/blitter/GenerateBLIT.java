package uk.bl.image.blitter;

import org.python.core.PyInteger;
import org.python.core.PyObject;
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

        // The exec() method executes strings of code
        interp.exec("import sys");
        interp.exec("print sys");

        // Set variable values within the PythonInterpreter instance
        interp.set("a", new PyInteger(42));
        interp.exec("print a");
        interp.exec("x = 2+2");

        // Obtain the value of an object from the PythonInterpreter and store it
        // into a PyObject.
        PyObject x = interp.get("x");
        System.out.println("x: " + x);
        interp.exec("import jpylyzer");
        interp.exec("import jpylyzer.etpatch as ET");
        interp.exec("import genblit");
        interp.exec(
                "xml = genblit.build('src/test/resources/test-data/vdc_100022551931.0x000001')");
        PyString xmlString = (PyString) interp
                .eval("ET.tostring(xml, 'UTF-8', 'xml')");
        System.out.println("GOT: " + xmlString);

        interp.close();
		System.out.println("Java exiting");
	}

}
