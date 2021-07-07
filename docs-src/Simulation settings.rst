Project settings
------------------

Project settings in the "Simulation.toml" file are used to basic settings for a simulation. It is to be noted that if you choose to use the profile manager, make sure the simulation start and end time lie within the time the profiles span. For simulations time points outside the time range of an attahcde profile, the profile value will default to zero.


.. list-table:: 
   :widths: 25 25 500 500
   :header-rows: 1

   * - Field
     - Type
     - Default
     - Description
   * - start_time
     - str
     - "2016-1-1 00:00:00.0"
     - Defines the start time for the simulation. It uses the following format "YYYY-MM-DD HH:MM:SS.f" 
   * - end_time
     - str
     - "2016-1-2 00:00:00.0"
     - Defines the end time for the simulation. same format as 'start_time'
   * - time_step_min
     - float
     - 15.0
     - Defines simulation time step in minutes.
   * - max_iter
     - int
     - 20
     - Defines iteration limit for the CYME solver.
   * - error_tolerance
     - float
     - 0.001
     - Defines error tolerance for the CYME solver.
   * - simulation_type
     - str
     - "QSTS"
     - Defines simulation mode for CYME. Possible values "QSTS" for time-series simulation "Static" for load flow.
   * - cyme_installation_directory
     - str
     - "C:/Program Files (x86)/CYME/CYME"
     - Set federate name. Should be unique if multiple CYMEpy instances are participating in the cosimulation
   * - project_path
     - str
     - ""
     - Path to a valid CYMEpy project.
   * - sxst_file
     - str
     - ""
     - Name of the project file.
   * - mdb_file
     - str
     - ""
     - [OPTIONAL] File name of the profile mdb file. Only needed when using the internal profile manager.




