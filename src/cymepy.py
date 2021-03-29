from src.common import CORE_CYMEPY_PROJECT_FILES, DEVICES_WITH_MEMORY
from src.validators import validate_settings
from src.helics_interface import HELICS
from src.solver import Solver
from src.device_obj import DEVICE
import src.logger as Logger
import os

from src.profile_manager.hooks.HDF5 import ProfileManager

class cymeInstance:
    def __init__(self, SettingsDict, N=None):
        self.SystemStates = []
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
            cympy.app.ActivateRefresh(False)
            self.cympy = cympy
        except:
            self.__Logger.error('Cyme module not found.')
            raise Exception("Cyme module not found.")

        if self.settings["profiles"]["use_profiles"] and self.settings["profiles"]["use_internal_profile_manager"]:
            if self.settings['project']["mdb_file"]:
                conn_info = cympy.db.ConnectionInformation()
                profiles_path = os.path.join(
                    self.settings['project']["project_path"],
                    'model',
                    self.settings['project']["mdb_file"]
                )
                assert os.path.exists(profiles_path), f"The profiles file: {profiles_path} does not exist"
                conn_info.LoadProfile = cympy.db.MDBDataSource()
                conn_info.LoadProfile.Path = profiles_path
                cympy.db.Connect(conn_info)

        print(dir(cympy.enums.DeviceType()))
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

        self.simObj = Solver(cympy, SettingsDict, self.__Logger)
        self.profile_manager = ProfileManager(self.cympy, self.simObj, self.settings, self.__Logger)
        self.devices = {}
        if self.settings['project']["simulation_type"] == "QSTS":
            for elm_type in DEVICES_WITH_MEMORY:
                self.devices[elm_type] = self.get_devices(elm_type, DEVICES_WITH_MEMORY[elm_type])

        #print(self.devices)

        if self.settings["helics"]["cosimulation_mode"]:
            self.HI = HELICS(SettingsDict, self.cympy, self.simObj, self.__Logger)

        return

    def get_devices(self, elm_type, var_list):
        enumerator = getattr(self.cympy.enums.DeviceType, elm_type)
        devices = self.cympy.study.ListDevices(enumerator)
        #print(devices)
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
            incFlag = self.runStep(incFlag)
            if incFlag:
                step += 1
        return

    def runStep(self, increment_flag):
        self.restore_states()
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

        self.save_states()

        if self.settings['helics']['cosimulation_mode']:
            increment_flag, helics_time = self.HI.request_time_increment()
            self.HI.update_publications()
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

if __name__ == "__main__":
    import toml
    Settings = toml.load(open(r"C:\Users\alatif\Desktop\CYMEPY\examples\LFwithProfiles\Settings.toml"))
    instance = cymeInstance(Settings)
    instance.runSimulation()