from cymepy.common import CORE_CYMEPY_PROJECT_FILES, DEVICES_WITH_MEMORY
from cymepy.validators import validate_settings
from cymepy.helics_interface import HELICS
from cymepy.solver import Solver
from cymepy.device_obj import DEVICE
import cymepy.logger as Logger
import os

class cymeInstance:
    def __init__(self, SettingsDict, N=None):
        self.SystemStates = []
        self.step = 0
        self.settings = validate_settings(SettingsDict, CORE_CYMEPY_PROJECT_FILES.SIMULATION_FILE)
        LoggerTag = 'CymeInstance' if N == None else 'CymeInstance_' + str(N)
        self.__Logger = Logger.getLogger(
            LoggerTag,
            LoggerOptions=SettingsDict["logger"],
            logger_path=os.path.join(self.settings["project"]["project_path"], 'logs')
        )

        import sys
        sys.path.append(SettingsDict["project"]['cyme_installation_directory'])
        self.__Logger.info('Creating Cyme instance')
        try:
            import cympy
            import cympy.rm
            import cympy.db

            print(dir(cympy.enums.DeviceType))
          
            cympy.app.ActivateRefresh(False)
            self.cympy = cympy
        except:
            self.__Logger.error('Cyme module not found.')
            raise Exception("Cyme module not found.")

        if self.settings["profiles"]["use_profiles"] and self.settings["profiles"]["use_internal_profile_manager"]:
            if self.settings['project']["profiles_mdb_file"]:
                #cympy.db.Disconnect()
                self.__Logger.info('Connecting to CYME profile database')
                conn_info = cympy.db.ConnectionInformation()
                profiles_path = os.path.join(
                    self.settings['project']["project_path"],
                    'model',
                    self.settings['project']["profiles_mdb_file"]
                )
                assert os.path.exists(profiles_path), f"The profiles file: {profiles_path} does not exist"
                conn_info.LoadProfile = cympy.db.MDBDataSource()
                conn_info.LoadProfile.Path = profiles_path
                cympy.db.Connect(conn_info)
               
                if not cympy.db.IsConnected():
                    self.__Logger.warning(f'Failed to connect to database')
                else:
                    self.__Logger.info(f'Database connected sucessfully')
                

        self.__Logger.info(cympy.version + ' created sucessfully.')
        self.projectPath = os.path.join(
            SettingsDict["project"]['project_path'],
            "model",
            SettingsDict["project"]['sxst_file']
        )

        if os.path.exists(self.projectPath):
            try:
                cympy.study.Open(self.projectPath)
            except Exception as exception:
                raise Exception(f'Unable to load the project at: {self.projectPath}\n{exception}')
            self.__Logger.info('Project loaded successfully.')
        else:
            raise Exception(f"Project path: {self.projectPath} does not exist")

        self.check_sources()
        self.simObj = Solver(cympy, SettingsDict, self.__Logger)

        if self.settings["profiles"]["use_profiles"] and not self.settings["profiles"]["use_internal_profile_manager"]:
            if self.settings["profiles"]["source_type"] == "h5":
                from cymepy.profile_manager.hooks.HDF5 import ProfileManager
                self.profile_manager = ProfileManager(self.cympy, self.simObj, self.settings, self.__Logger)
            elif self.settings["profiles"]["source_type"] == "mdb":
                from cymepy.profile_manager.hooks.ACCESS import ProfileManager
                self.profile_manager = ProfileManager(self.cympy, self.simObj, self.settings, self.__Logger)

        self.devices = {}
        if self.settings['project']["simulation_type"] == "QSTS":
            for elm_type in DEVICES_WITH_MEMORY:
                self.devices[elm_type] = self.get_devices(elm_type, DEVICES_WITH_MEMORY[elm_type])

        self.export_manager = self.get_export_manager()

        if self.settings["helics"]["cosimulation_mode"]:
            self.HI = HELICS(SettingsDict, self.cympy, self.simObj, self.__Logger)

        return

    def check_sources(self):
        sources = self.cympy.study.ListDevices(self.cympy.enums.DeviceType.Source)
        i = 1
        if not sources:
            source_nodes = self.cympy.study.ListNodes(self.cympy.enums.NodeType.SourceNode)
            sections = self.cympy.study.ListSections()
            networks = self.cympy.study.ListNetworks()
            for section in sections:
                for node in source_nodes:
                    if node.ID == section.FromNode.ID: 
                        nodeID = node.ID.split("-")[0]
                        for network in networks:
                            red_network = network.split(">")[1]
                            if red_network == nodeID:
                                source = self.cympy.study.AddDevice(
                                    f"NEW-SOURCE-{i}", 
                                    self.cympy.enums.DeviceType.Source, 
                                    section.ID, 
                                    "DEFAULT"
                                )
                                #source.SetValue(12.47, 'OperatingVoltageA')
                                #source.SetValue(12.47, 'OperatingVoltageB')
                                #source.SetValue(12.47, 'OperatingVoltageC')
                                self.__Logger.info(f"Source added to network {network} at section {section}")
                                i += 1
        #sources = self.cympy.study.ListDevices(self.cympy.enums.DeviceType.Source)
        return


    def get_devices(self, elm_type, var_list):
        enumerator = getattr(self.cympy.enums.DeviceType, elm_type)
        devices = self.cympy.study.ListDevices(enumerator)

        device_dict = {}
        for device in devices:
            device_dict[device.DeviceNumber] = DEVICE(self.cympy, device, var_list)
        return device_dict

    def UpdateLoadProfiles(self, ProfilePath):

        return

    def runSimulation(self):
        Steps, StartTime, EndTime = self.simObj.SimulationSteps()
        self.__Logger.info('Running simulation from time {} to {} at a time increment of {} minute/s.'.format(
            StartTime, EndTime, self.settings['project']['time_step_min']
        ))
        step = 0
        incFlag = False
        while step < Steps:
            if self.step != step and step != 0:
                self.restore_states()
            incFlag = self.runStep(incFlag)
            if incFlag:
                self.export_manager.update()
                self.save_states()
                step += 1
            self.step = step
        self.export_manager.export()
        return

    def runStep(self, increment_flag):
        if self.settings["profiles"]["use_profiles"] and not self.settings["profiles"]["use_internal_profile_manager"]:
            self.profile_manager.update()
        if self.settings['helics']['cosimulation_mode']:
            self.HI.update_subscriptions()
            pass

        if self.settings['helics']['cosimulation_mode']:
            if increment_flag:
                self.simObj.increment()
            else:
                self.simObj.resolve()
        else:
            self.simObj.increment()
        if self.settings['helics']['cosimulation_mode']:
            increment_flag, helics_time = self.HI.request_time_increment()
            self.HI.update_publications()
            self.HI.publish()
            return increment_flag
        else:
            return True

    def save_states(self):
        for cName, devices in self.devices.items():
            for dName, device in devices.items():
                device.save_state()
        return

    def restore_states(self):
        for cName, devices in self.devices.items():
            for dName, device in devices.items():
                device.restore_state()
        return

    def get_export_manager(self):
        if self.settings['Exports']['export_file_type'] == "csv":
            from cymepy.export_manager.hooks.csv_writer import Writer
            export_manager = Writer(self.cympy, self.simObj, self.settings, self.__Logger)
        elif self.settings['Exports']['export_file_type'] == "h5":
            from cymepy.export_manager.hooks.h5_writer import Writer
            export_manager = Writer(self.cympy, self.simObj, self.settings, self.__Logger)
        elif self.settings['Exports']['export_file_type'] == "json":
            from cymepy.export_manager.hooks.JSON_writer import Writer
            export_manager = Writer(self.cympy, self.simObj, self.settings, self.__Logger)
        return export_manager

if __name__ == "__main__":
    import toml
    Settings = toml.load(open(r"C:\Users\alatif\Desktop\Cymepy\examples\LFwithProfiles\Settings.toml"))
    instance = cymeInstance(Settings)
    instance.runSimulation()