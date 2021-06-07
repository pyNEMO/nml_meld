Installation
============
This page provides a guide to installing pynemo_namelist_reader

Dependencies
^^^^^^^^^^^^

1. Python 3.7

Anaconda
^^^^^^^^

Using conda: pynemo_namelist_reader supports Win64, OSX and Linux.

.. note:: It is recommended to create a seperate virtual environment for pynemo_namelist_reader
          Please follow the instructions on doing this at:
          https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
::

   conda install -c channel pynemo_namelist_reader

This will install pynemo_namelist_reader and its dependencies.

From Source
^^^^^^^^^^^

Installing pynemo_namelist_reader from source. Download all the dependencies and
clone the source code from GitHub and run the setup.

::

   git clone https://github.com/jdha/PyNEMO_namelist_tool.git
   cd PyNEMO_namelist_tool
   python setup.py build
   python setup.py install

.. note:: If building from source in the Anaconda environment all dependencies can
          be installed using conda. 

