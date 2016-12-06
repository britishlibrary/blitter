import os
import luigi
import luigi.contrib.hadoop
import urllib
import zipfile
import logging
import tempfile
import xml.etree.ElementTree as ET

import jpylyzer.jpylyzer as jpylyzer # Imported from https://github.com/britishlibrary/jpylyzer
import genblit

logger = logging.getLogger('luigi-interface')


class blit(luigi.Config):
    """
    Configuration class for these tasks

    Parameters:
        url_template = String template to construct a URL from an identifier.

    """
    url_template = luigi.Parameter()


class ExternalListFile(luigi.ExternalTask):
    """
    Example of a possible external data dump
    To depend on external targets (typically at the top of your dependency graph), you can define
    an ExternalTask like this.
    """
    input_file = luigi.Parameter()

    def output(self):
        """
        Returns the target output for this task.
        In this case, it expects a file to be present in HDFS.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.contrib.hdfs.HdfsTarget(self.input_file)


class RunJpylyzer(luigi.contrib.hadoop.JobTask):
    """
    This class takes a list of identifiers for JPEG2000 files, then downloads them, and then runs Jpylyzer on them
    to extract metadata about the file.

    The output is of the form:

        <identifier><tab><jpylyzer-xml-as-string><newline>
        ....

    Parameters:
        input_file: The file (on HDFS) that contains the list of identifiers.
    """
    input_file = luigi.Parameter()

    def output(self):
        return luigi.contrib.hdfs.HdfsTarget("blitter/jpylyzer.tsv")

    def requires(self):
        return ExternalListFile(self.input_file)

    def extra_modules(self):
        return [jpylyzer,genblit]

    def extra_files(self):
        return ["luigi.cfg"]

    def mapper(self, line):
        """
        Each line should be an identifier of a JP2 file, e.g. 'vdc_100022551931.0x000001'

        In the mapper we download, and then jpylyze it

        :param line:
        :return:
        """

        # Ignore blank lines:
        if line == '':
            return

        try:
            # Create to temp file:
            (jp2_fd, jp2_file) = tempfile.mkstemp()

            # Construct URL and download:
            id = line.replace("ark:/81055/","")
            download_url = blit().url_template % id
            logger.warning("Downloading: %s " % download_url)
            # Download via proxy, currently hard-coded and in-memory:
            proxies = {'http': 'http://192.168.1.1:3127'}
            data = urllib.urlopen(download_url, proxies=proxies).read()
            with open(jp2_file,"wb") as f:
                f.write(data)

            # Jpylyser-it:
            jpylyzer_xml = jpylyzer.checkOneFile(jp2_file)

            # Map to a string, and strip out newlines:
            jpylyzer_xml_out = ET.tostring(jpylyzer_xml, 'UTF-8', 'xml')
            jpylyzer_xml_out = jpylyzer_xml_out.replace('\n', ' ').replace('\r', '')

            # Delete the temp file:
            os.remove(jp2_file)
        except Exception as e:
            jpylyzer_xml_out = "FAILED! %s" % e
            raise(e)

        # And return:
        yield line, jpylyzer_xml_out

    def reducer(self, key, values):
        """
        A pass-through reducer.

        :param key:
        :param values:
        :return:
        """
        for value in values:
            yield key, value
        # An actual reducer:
        #yield key, sum(values)


class GenerateBlit(luigi.contrib.hadoop.JobTask):
    """
    This class takes the output from Jpylyzer and transforms it into 'blit' XML.

    """
    input_file = luigi.Parameter()

    def requires(self):
        return RunJpylyzer(self.input_file)

    def output(self):
        # FIXME use os.dirname to generate output filename from input filename (also above too)
        return luigi.contrib.hdfs.HdfsTarget("blitter/blit.tsv")

    def extra_modules(self):
        return [jpylyzer,genblit]

    def mapper(self, line):
        """
        Each line should be an identifier of a JP2 file, e.g. 'vdc_100022551931.0x000001' followed by a string
        that is the XML output from Jpylyzer.

        In the mapper we re-parse, then convert to blit for output.

        :param line:
        :return:
        """

        # Ignore blank lines:
        if line == '':
            return

        try:
            # Split the input:
            id, jpylyzer_xml_out = line.strip().split("\t",1)

            # Re-parse the XML:
            ET.register_namespace("", "http://openpreservation.org/ns/jpylyzer/")
            jpylyzer_xml = ET.fromstring(jpylyzer_xml_out)

            # Convert to blit xml:
            blit_xml = genblit.to_blit(jpylyzer_xml)

            # Map to a string, and strip out newlines:
            blit_xml_out = ET.tostring(blit_xml, 'UTF-8', 'xml')
            blit_xml_out = blit_xml_out.replace('\n', ' ').replace('\r', '')

        except Exception as e:
            id = line
            blit_xml_out = "FAILED! %s" % e

        # And return both forms:
        yield id, blit_xml_out

    def reducer(self, key, values):
        """
        A pass-through reducer.

        :param key:
        :param values:
        :return:
        """

        for value in values:
            yield key, value
        # An actual reducer:
        #yield key, sum(values)


class GenerateBlitZip(luigi.Task):
    """
    ...
    """
    input_file = luigi.Parameter()

    def requires(self):
        return GenerateBlit(self.input_file)

    def output(self):
        return luigi.LocalTarget("%s.zip" % self.input_file)

    def run(self):
        with zipfile.ZipFile(self.output(),'w') as out_file:
            with self.input().open('r') as in_file:
                for line in in_file:
                    id, xmlstr = line.strip("\t",1).split()
                    out_file.writestr(id, xmlstr)


if __name__ == '__main__':
    luigi.run(['GenerateBlitZip', '--input-file', 'test-input.txt', '--local-scheduler'])
