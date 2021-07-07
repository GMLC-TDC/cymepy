The HELICS interface
--------------------

Hierarchical Engine for Large-scale Infrastructure Co-Simulation (HELICS) is an open-source co-simulation framework is designed to integrate simulators designed for separate TDC domains to simulate regional and interconnection-scale power system behaviors at unprecedented levels of detail and speed. HELICS has bindings for a few programming language. CYMEpy uses CYME's Pytyhon API and HELICS's Python bindings to interface with HELICS. HELICS documentations can be found here: https://helics.org/introduction/.
   
Co-simulation settings
======================

Settings for the HELICS interface can be setup within the "Settings.toml" file  in the CYMEpy project.


.. list-table:: 
   :widths: 25 25 25 50
   :header-rows: 1

   * - Field
     - Type
     - Default
     - Description
   * - cosimulation_mode
     - bool
     - false
     - Set to 'true' to enable the HELICS interface  
   * - coiter_mode
     - bool
     - false
     - Set to 'true' to run HELICS in coiteration mode. By default HELICS will execute a loosely coupled cosimulation  
   * - coiter_error_tolerance
     - float
     - 0.1
     - Set error tolerance for coiteration. Coiteration loop will exit if change if subscription values summed across subscriptions is less than the threshold defined
   * - max_coiter
     - int
     - 20
     - Set maximum coiteration limit. Coiteration loop will exit if coiteration exceeds the set limit. A warning will be logged if convergance tolerance is not reached
   * - broker
     - str
     -  "127.0.0.1"
     - Set IP for of the broker, CYMEpy federate should be connecting to
   * - broker_port
     - int
     - 50001
     - Set port for of the broker, CYMEpy federate should be connecting to
   * - federate_name
     - str
     - "CYME"
     - Set federate name. Should be unique if multiple CYMEpy instances are participating in the cosimulation
   * - time_delta
     - float
     - 0.01
     - Set minimum time step for the HELICS cosimulation
   * - core_type
     - str
     - "ZMQ"
     - Choose communication core type. For more information please visit https://docs.helics.org/en/latest/configuration/CoreTypes.html
   * - uninterruptible
     - bool
     - true
     - If set to true the federate can only return time expressly requested (or the next valid time after the requested time). For more information please visi https://docs.helics.org/en/latest/configuration/Timing.html?highlight=uninterruptible
   * - helics_logging_level
     - int
     - 5
     - Set verbose level for the HELICS logger. Enumeration documentation can be found here: https://docs.helics.org/en/latest/c-api-reference/index.html?highlight=helics_logging_level#_CPPv328helics_log_level_connections

The final step is to setup publications and subscriptions for the co-simulation


Setting up publications
=======================

For setting up the helics publications, users need to create / populate "Publications.toml" file in the project directory. Publications can be defined using the following format ::

	[["<CYME model type>"]]
	"regex_filter" = "\\b\\d\\d.\\d"
	"properties" = [list of valid CYME keyword or properties]

Working example of a populated "Publications.toml" can be found here https://github.com/GMLC-TDC/cymepy/blob/master/examples/ieee13node/Publications.toml.

Regular expressions can be used to setup up publications for a subbet of model type (e.g. if you want to interface a subset of connected loads). If regex_filter field is kept empty, publications will be created for elements of the named model type. <CYME model type> should follow CYME naming convention (e.g. InductionMotor, Transformer, DistributedLoad,Source).

Publication naming convention follow by CYMEpy is as follows. ::

	
	<Federate name>.<CYME model type>.<CYME model name>.<property name>


Where, <Federate name> is defined in the "Settings.toml" file.  <CYME model type> come from the publication definations in the "Publications.toml" file and <property name> comes from the list of properties defined for each publication defination. 


If for example a CYMEpy model has only one source named "test" and the federate name is "CYME", defining the following publication defination in the toml file::

	[["Source"]]
	"regex_filter" = ""
	"properties" = ["KWTOT", "KVARTOT", "OperatingVoltageA"] 

will create three publications for the CYMEpy federate. ::

	CYME.Source.test.KWTOT
	CYME.Source.test.KVARTOT
	CYME.Source.test.OperatingVoltageA


This interface allows users to setup HELICS cosimulations without writing a single line of code.

Setting up subscriptions
========================

or setting up the helics subscriptions, users need to create / populate "Subscriptions.toml" file in the project directory. Subscriptions can be defined using the following format ::

	[["<CYME model type>.<CYME model name>"]]
	property = "<valid CYME keyword or property>"
	subscription = "<Subscription tag>" 
	multiplier = <float>
	
<Subscription tag> is a publication tag from different federate this federate needs to subscribe to. A multiplier can be used to scale the subscription before updating the object value. The multiplier allows user to match boundary conditions at the first time step in the simulation.

If the user wants a subscription named "voltageC" to update the phase C voltage of the source model named "test", user can setup a subscription in the following format ::

	[["Source.test"]]
	property = "OperatingVoltageC"
	subscription = "voltageC"
	multiplier = 1 
	
This lets CYMEPY know that "voltageC" will be user to update the property "OperatingVoltageC" of element "Source.test" in the CYME model.
