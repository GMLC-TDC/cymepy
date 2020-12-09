from src.validators import ValidateProjectSettings
from src.helics_interface import HELICS
from src.solver import Solver
import src.logger as Logger
import os

class cymeInstance:
    def __init__(self, SettingsDict, N=None):
        self.SystemStates = []
        self.settings = SettingsDict
        ValidateProjectSettings(SettingsDict)

        LoggerTag = 'CymeInstance' if N == None else 'CymeInstance_' + str(N)
        self.__Logger = Logger.getLogger(LoggerTag, LoggerOptions=SettingsDict["Logger options"])

        import sys
        sys.path.append(SettingsDict["Project"]['Cyme Installation Directory'])
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
            SettingsDict["Project"]['Project Path'],
            SettingsDict["Project"]['Active Project'],
            "model",
            SettingsDict["Project"]['SXST File']
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
        self.HI = HELICS(SettingsDict, self.cympy, self.simObj, self.__Logger)

        return

    def UpdateLoadProfiles(self, ProfilePath):

        return

    def runSimulation(self):
        Steps, StartTime, EndTime = self.simObj.SimulationSteps()
        self.__Logger.info('Running simulation from time {} to {} at a time increment of {} minute/s.'.format(
            StartTime, EndTime, self.settings['Project']['Step resolution (min)']
        ))
        step = 0
        incFlag = False
        while step < Steps:
            incFlag = self.runStep(incFlag)
            if incFlag:
                step += 1
        return

    def runStep(self, increment_flag):
        if self.settings['Helics']['Co-simulation Mode']:
            self.HI.update_subscriptions()

        if self.settings['Helics']['Co-simulation Mode']:
            if increment_flag:
                self.simObj.increment()
            else:
                self.simObj.resolve()
        else:
            self.simObj.increment()

        if self.settings['Helics']['Co-simulation Mode']:
            increment_flag, helics_time = self.HI.request_time_increment()
            self.HI.update_publications()
            return increment_flag

        return


if __name__ == "__main__":
    import toml
    Settings = toml.load(open(r"C:\Users\alatif\Desktop\CYMEPY\examples\Example1\Settings.toml"))
    instance = cymeInstance(Settings)
    instance.runSimulation()