.. cymepy documentation master file, created by
   sphinx-quickstart on Tue Jul  6 12:17:56 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


About CYMEpy
===========
CYMEpy is a high-level Python package that provides users HELICS bindings for CYMEDIST, CYME's distribution system simulator.

Installation
============

CYMEpy can be installed by typing the following command on the command prompt::

	pip install cymepy
	
Alternately, if you choose to clone the git repo from https://github.com/GMLC-TDC/cymepy , use the followiing commands to build the module and install it. ::

	python setup.py -build
	python setup.py -install


Running existing CYMEpy example
================================
CYMEpy does come with a working HELICS example that can be used to test correct installation. The example can be found here https://github.com/GMLC-TDC/cymepy/tree/master/examples.

- Download the two folders 'helics_example_cyme' and 'ieee13node' to a local directory.
- Go into the folder 'helics_example_cyme' and run the 'run_dummy_federate.py' file using python. This will create a HELICS broker and a dummy federate with which CYMEpy federate will cosimulate.
- Next go into the 'ieee13node' example and open 'Settings.toml' file in a text editor.
- Update the 'project_path'. Here you will copy the path to your local 'ieee13node' folder.
- Update the 'cyme_installation_directory' if it differs from default. This is the path to CYMEDIST installation.
- Save and close the file.
- To run the simulation, in the command prompt type::

	cymepy rum {project path}
	



Setting up a  new CYMEpy project
================================
CYMEpy requires a specific directory format to define projects detailed below. ::

	~Projects 
            |__ <Project name>
            |      |__ model (Should contain CYME project files e.g. sxst file)	
            |      |__ exports (All simulation results will be exported to this folder)
            |      |__ logs (PyDSS logs will be exported to this folder)
            |      |__ Settings.toml (defines the simulation settings)
            |      |__ Exports.toml (defines all variables to be exported)
            |      |__ Mapping.toml~ (Populate to map profiles to spicific model e.g PV system or load)
            |      |__ Publications.toml^ (Populate to define HELICS publications)
            |      |__ Subscriptions.toml^ (Populate to define HELICS subscriptions)
            |__ IEEE_13node
            |__ EPRI_J1

- ~ OPTIONAL only required when 'use_internal_profile_manager' is set to true in the 'Settings.toml' file.
- ^ OPTIONAL only required when HELICS interface is enabled


Additional Documentation
========================

.. toctree::
   :maxdepth: 1

   Simulation settings 
   Managing profiles
   Exporting reults
   The HELICS interface
   
   
License
=======

BSD 3-Clause License

Copyright (c) 2020, Alliance for Sustainable Energy LLC, All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

- Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Contact
=======
Questions? Please send an email to aadil.latif@nrel.gov or aadil.latif@gmail.com



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
