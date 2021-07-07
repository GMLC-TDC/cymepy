Project settings
------------------

Project settings in the "Simulation.toml" file are used to basic settings for a simulation. It is to be noted that if you choose to use the profile manager, make sure the simulation start and end time lie within the time the profiles span. For simulations time points outside the time range of an attahcde profile, the profile value will default to zero.

- **start_time** - (str) defines the start time for the simulation. It uses the following format "YYYY-MM-DD HH:MM:SS.f" e.g "2016-1-2 00:00:00.0"
- **end_time** - (str) defines the end time for the simulation. same format as 'start_time'.
- **time_step_min** - (float) defines simulation time step in minutes.
- **max_iter** - (int) defines iteration limit for the CYME solver.
- **error_tolerance** - (float) defines error tolerance for the CYME solver.
- **simulation_type** - (str) defines simulation mode for CYME. Possible values "QSTS" for time-series simulation "Static" for load flow
- **cyme_installation_directory** - (str) path to CYME installation directory
- **project_path** - (str) path to a valis CYMEpy project.
- **sxst_file** - (str) name of teh project file.
- **mdb_file** - (str) [OPTIONAL] file name of the profile mdb file. Only needed when using the internal profile manager.



