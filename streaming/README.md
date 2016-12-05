streaming blitter
=================

This runs a streaming job on Hadoop, using the local Python 2.7 (additional) installion, and distributing the Python modules needed.

We use the luigi framework to help things run, e.g. packaging dependencies etc.

First the list of identifiers needs to be uploaded, then this task can be run on it.

This will run an example:

    $ python tasks.py
