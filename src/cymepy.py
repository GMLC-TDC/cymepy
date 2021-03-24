from src.common import CORE_CYMEPY_PROJECT_FILES
from src.validators import validate_settings
from src.helics_interface import HELICS
from src.solver import Solver
import src.logger as Logger
import os

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
            cympy.app.ActivateRefresh(True)
            self.cympy = cympy
        except:
            self.__Logger.error('Cyme module not found.')
            raise Exception("Cyme module not found.")

        self.__Logger.info(cympy.version + ' created sucessfully.')
        self.projectPath = os.path.join(
            SettingsDict["project"]['project_path'],
            "model",
            SettingsDict["project"]['sxst_file']
        )

        if self.settings["profiles"]["use_profiles"] and  self.settings["profiles"]["use_internal_profile_manager"]:
            if self.settings['project']["mdb_file"]:
                print(dir(cympy))
                conn_info = cympy.db.ConnectionInformation()
                profiles_path = os.path.join(
                    self.settings['project']["project_path"],
                    self.settings['project']["mdb_file"]
                )
                assert os.path.exists(profiles_path), f"The profiles file: {profiles_path} does not exist"
                conn_info.LoadProfile.Path = profiles_path
                cympy.db.Connect(conn_info)

        if os.path.exists(self.projectPath):
            try:
                cympy.study.Open(self.projectPath)
            except Exception as exception:
                raise Exception(f'Unable to load the project at: {self.projectPath}\n{exception}')
            self.__Logger.info('Project loaded successfully.')
        else:
            raise Exception(f"Project path: {self.projectPath} does not exist")

        self.simObj = Solver(cympy, SettingsDict, self.__Logger)
        if self.settings["helics"]["cosimulation_mode"]:
            self.HI = HELICS(SettingsDict, self.cympy, self.simObj, self.__Logger)
        return

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
            return increment_flag
        else:
            return True

if __name__ == "__main__":
    import toml
    Settings = toml.load(open(r"C:\Users\alatif\Desktop\CYMEPY\examples\Example1\Settings.toml"))
    instance = cymeInstance(Settings)
    instance.runSimulation()