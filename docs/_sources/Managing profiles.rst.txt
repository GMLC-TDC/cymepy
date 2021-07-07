Profile management
------------------

CYMEpy allows users to user either use CYME's internal profile manager or use the profile management build for CYMEpy. 
To enable profile for a simulaion run set "use_profiles" to true. To use the internal profile manager set "use_internal_profile_manager" to true.


Using HDF5 files
=================
- To use HDF5 files set source_type to "h5". for a working example see: https://github.com/GMLC-TDC/cymepy/blob/master/examples/ieee13node/Profiles.hdf5
- provide path to the HDF5 file in the "source" field.
- If the HDF5 file is placed within the project folder, set is_relavtive_path to true. Only file name is then required in the "source" field
- Profiles in the HDF5 file can be attached to CYME models using the "Mapping.toml" file.

A profile can be attached to multiple objects. User can use a multipler, normalize or interpolate. An example is shown below. ::

	[[<profile type>.<profile name>]]
	"object" = "<CYME model type>.<model name>"
	"multiplier" = 170.0
	"normalize" = true
	"interpolate" = true
	
For a working example see ::
	
	https://github.com/GMLC-TDC/cymepy/blob/master/examples/ieee13node/Mapping.toml


Using ACCESS files
=================
- To use HDF5 files set source_type to "mdb". 
- In the "source" field provide file path for the mdb file.

For setting up ACCESS profiles, additional information is required to complete  the setup. this includes providing driver name and db password (if the file has one). Finally mapping between tables and object type should be populated.An example is shown below. ::

	[profiles]
	use_profiles = true
	use_internal_profile_manager = false
	source_type = "mdb"
	source = "LFwithProfiles.mdb"
	is_relavtive_path = true
	[profiles.settings]
	driver = "Microsoft Access Driver (*.mdb)"
	password = ""
	[profiles.tables]
	SpotLoad = "LOAD_E_1HOUR"
	Photovoltaic = "GENERATOR_E_1HOUR"


Extending support for other file types
======================================

CYMEpy currently supports MS Access and HDF5 files. Users have the option of extending profile management interface by wring a class that inherits from abstract classes "BaseProfileManager" and "BaseProfile" in https://github.com/GMLC-TDC/cymepy/blob/master/cymepy/profile_manager/base_definations.py. For implmentation examples see.
	
- https://github.com/GMLC-TDC/cymepy/blob/master/cymepy/profile_manager/hooks/ACCESS.py
- https://github.com/GMLC-TDC/cymepy/blob/master/cymepy/profile_manager/hooks/HDF5.py