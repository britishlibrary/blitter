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


