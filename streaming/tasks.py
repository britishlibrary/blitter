import luigi
import luigi.contrib.hadoop
import urllib
import tempfile
import xml.etree.ElementTree as ET

import jpylyzer.jpylyzer as jpylyzer # Imported from https://github.com/britishlibrary/jpylyzer
import genblit

class GenerateBlit(luigi.contrib.hadoop.JobTask):
    input_file = luigi.Parameter()

    def output(self):
        return luigi.contrib.hdfs.HdfsTarget("data/artist_streams_%s.tsv" % self.date_interval)

    #def requires(self):
    #    return [StreamsHdfs(date) for date in self.date_interval]

    def mapper(self, line):
        '''
        Each line should be an identifier of a JP2 file.

        In the mapper we download, and then jpylyze it, then convert to blit for output.

        :param line:
        :return:
        '''

        # Download to temp file:
        jp2_file = tempfile.mkstemp()
        urllib.urlretrieve(line, jp2_file)

        # Jpylyser-it:
        jpylyzer_xml = jpylyzer.checkOneFile(jp2_file)

        # Convert to blit xml:
        blit_xml = genblit.to_blit(jpylyzer_xml)

        # Map to a string:
        xmlOut = ET.tostring(blit_xml, 'UTF-8', 'xml')

        # Delete the temp file:
        jp2_file.delete()

        # And return:
        yield line, xmlOut

    def reducer(self, key, values):
        # Pass-through reducer:
        for value in values:
            yield key, value
        # An actual reducer:
        #yield key, sum(values)
