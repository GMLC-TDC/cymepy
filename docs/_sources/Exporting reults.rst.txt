Exporting results
------------------

CYMEpy currently supports exporting results in the followinf formats
	- CSV (comma seperated text files)
	- HDF5
	- JSON
	
Users can choose a particular format by setting teh following fields in the "Settings.toml" file.  ::
	
	[Exports]
	in_memory = true
	export_file_type = "h5"

Possible options for "export_file_type" are  "h5", "json" and "csv". Users have the option of extending the result management interface by wring a class that inherits from abstract class "ExportManager" in https://github.com/GMLC-TDC/cymepy/blob/master/cymepy/export_manager/base_definations.py. For implmentation examples see. 
	
- https://github.com/GMLC-TDC/cymepy/blob/master/cymepy/export_manager/hooks/csv_writer.py
- https://github.com/GMLC-TDC/cymepy/blob/master/cymepy/export_manager/hooks/JSON_writer.py
- https://github.com/GMLC-TDC/cymepy/blob/master/cymepy/export_manager/hooks/h5_writer.py