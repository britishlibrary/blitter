streaming blitter
=================

This runs a streaming job on Hadoop, using the local Python 2.7 (additional) installion, and distributing the Python modules needed.

We use the luigi framework to help things run, e.g. packaging dependencies etc.

Quick start
-----------

First the list of identifiers needs to be uploaded, then this task can be run on it. e.g.

    $ hadoop fs -copyFromLocal test-input.txt .

Then set up a suitable Python environment and install the code and any necessary dependencies:

   $ virtualenv -p python2.6 venv27-blitter
   $ source venv27-blitter/bin/activate
   $ python setup.py install

This will run an example, directly from the source folder:

    $ python tasks.py

Or invoke luigi itself, which will run the installed version if the task:

    $ luigi GenerateBlit --input-file test-input.txt --local-scheduler

This runs two separate tasks. The first task, called `RunJpylyzer`, is the task that downloads the image and runs
Jpylyzer on it. The resulting XML is stored as e.g. `blitter/jpylyzer.tsv/part-*`, and so we can run various analyses
over this output without re-downloading the images.

This output data is the pre-requisite for the GenerateBlit task, which reads the XML in and transforms it into 'blit'
XML, which looks like this:

```xml
<?xml version="1.0"?>
<blit:blimagetech xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xsi:schemaLocation="http://bl.uk/namespaces/blit ./blit_v02.xsd" xmlns:blit="http://bl.uk/namespaces/blit">
  <image offset="0">
    <blit:dimension>
      <blit:width unit="pixel">2124</blit:width>
      <blit:height unit="pixel">2819</blit:height>
    </blit:dimension>
    <blit:resolution>
      <blit:x unit="ppi">300</blit:x>
      <blit:y unit="ppi">300</blit:y>
    </blit:resolution>
    <blit:channels>1</blit:channels>
    <blit:bitsperchannel>8</blit:bitsperchannel>
    <blit:format xsi:type="blit:jpeg2000">
      <blit:jp2_compression type="JPEG2000_Lossy" />
      <blit:jp2_codeblocksize>
        <blit:jp2_cbx>64</blit:jp2_cbx>
        <blit:jp2_cby>64</blit:jp2_cby>
      </blit:jp2_codeblocksize>
      <blit:jp2_layers>12</blit:jp2_layers>
      <blit:jp2_progressionorder>RPCL</blit:jp2_progressionorder>
      <blit:jp2_levels>6</blit:jp2_levels>
      <blit:jp2_tile_dimensions>
        <blit:jp2_tile dwt_level="1,2,3,4,5,6">
          <blit:jp2_tile_x>2124</blit:jp2_tile_x>
          <blit:jp2_tile_y>2819</blit:jp2_tile_y>
        </blit:jp2_tile>
      </blit:jp2_tile_dimensions>
      <blit:jp2_precincts>
        <blit:jp2_precinct dwt_level="1,2">
          <blit:jp2_precinct_x>256</blit:jp2_precinct_x>
          <blit:jp2_precinct_y>256</blit:jp2_precinct_y>
        </blit:jp2_precinct>
        <blit:jp2_precinct dwt_level="3,4,5,6">
          <blit:jp2_precinct_x>128</blit:jp2_precinct_x>
          <blit:jp2_precinct_y>128</blit:jp2_precinct_y>
        </blit:jp2_precinct>
      </blit:jp2_precincts>
    </blit:format>
  </image>
</blit:blimagetech>
```


