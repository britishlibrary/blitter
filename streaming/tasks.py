import os
import luigi
import luigi.contrib.hadoop
import urllib
import logging
import tempfile
import xml.etree.ElementTree as ET

import jpylyzer.jpylyzer as jpylyzer # Imported from https://github.com/britishlibrary/jpylyzer
import genblit

logger = logging.getLogger('luigi-interface')

class ExternalListFile(luigi.ExternalTask):
    input_file = luigi.Parameter()
    """
    Example of a possible external data dump
    To depend on external targets (typically at the top of your dependency graph), you can define
    an ExternalTask like this.
    """

    def output(self):
        """
        Returns the target output for this task.
        In this case, it expects a file to be present in HDFS.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.contrib.hdfs.HdfsTarget(self.input_file)


class GenerateBlit(luigi.contrib.hadoop.JobTask):
    input_file = luigi.Parameter()

    def output(self):
        return luigi.contrib.hdfs.HdfsTarget("data/blit.tsv")

    def requires(self):
        return ExternalListFile(self.input_file)

    def extra_modules(self):
        return [jpylyzer, genblit]

    def mapper(self, line):
        '''
        Each line should be an identifier of a JP2 file, e.g. 'vdc_100022551931.0x000001'

        In the mapper we download, and then jpylyze it, then convert to blit for output.

        :param line:
        :return:
        '''


        # Ignore blank lines:
        if line == '':
            return

        try:
            # Download to temp file:
            (jp2_fd, jp2_file) = tempfile.mkstemp()
            #download_url = \
            #    "https://github.com/anjackson/blitter/blob/master/jython/src/test/resources/test-data/%s?raw=true" % line
            download_url = "http://nellie-private.bl.uk:14000/webhdfs/v1/user/anjackson/%s?op=OPEN&user.name=hdfs" % line
            logger.warning(download_url)
            (tempfilename, headers) = urllib.urlretrieve(download_url, jp2_file)

            # Jpylyser-it:
            jpylyzer_xml = jpylyzer.checkOneFile(jp2_file)

            # Convert to blit xml:
            blit_xml = genblit.to_blit(jpylyzer_xml)

            # Map to a string, and strip out newlines:
            xml_out = ET.tostring(blit_xml, 'UTF-8', 'xml')
            xml_out = xml_out.replace('\n','')

            logger.info(xml_out)

            # Delete the temp file:
            os.remove(jp2_file)
        except Exception as e:
            xml_out = "FAILED! %s" % e

        # And return:
        yield line, xml_out

    def reducer(self, key, values):
        # Pass-through reducer:
        for value in values:
            yield key, value
        # An actual reducer:
        #yield key, sum(values)


if __name__ == '__main__':
    luigi.run(['GenerateBlit', '--input-file', 'test-input.txt', '--local-scheduler'])
