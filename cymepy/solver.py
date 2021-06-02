from datetime import datetime, timedelta
from cymepy.common import DATE_FORMAT
import math
import os

class Solver:

    def __init__(self, cymepy, settings, logger):
        self.Settings = settings
        self._Logger = logger
        self.cymepy = cymepy

        self._mStepRes = settings['project']['time_step_min']
        StartTimeMin = settings['project']['start_time']
        EndTimeMin = settings['project']['end_time']

        self._Time = datetime.strptime(StartTimeMin, DATE_FORMAT)
        self._StartTime = self._Time
        self._EndTime = datetime.strptime(EndTimeMin, DATE_FORMAT)

        if settings['project']["simulation_type"] == "QSTS":
            if self.Settings['profiles']["use_internal_profile_manager"]:

                self.solverObj = cymepy.sim.LoadFlowWithProfiles()
                self.solverObj.SetValue("SingleTimeMode", "Parameters.TimeParametersMode")
                self.loadflowSettings(cymepy.sim.LoadFlow())

            else:
                self.solverObj = cymepy.sim.LoadFlow()
                self.loadflowSettings(self.solverObj)
        elif settings['project']["simulation_type"] == "Static":
            self.solverObj = cymepy.sim.LoadFlow()
            self.loadflowSettings(self.solverObj)

        self._Logger.debug("Solver object created.")
        return

    def loadflowSettings(self, lf):
        lf.SetValue('VoltageDropUnbalanced', 'ParametersConfigurations[0].AnalysisMode')
        lf.SetValue(self.Settings['project']["max_iter"],
                                'ParametersConfigurations[0].MaximumIterations')
        lf.SetValue(self.Settings['project']["error_tolerance"],
                                'ParametersConfigurations[0].VoltageTolerance')
        return

    def increment(self):
        if self.Settings['project']["simulation_type"] == "QSTS":
            if self.Settings['profiles']["use_profiles"]:
                if self.Settings['profiles']["use_internal_profile_manager"]:
                    self.solverObj.SetValue(int(self._Time.timestamp()), "Parameters.SingleTime")
                    self.solverObj.Run()
                    #self._Logger.debug(f"CYME internal time: {self._Time}")
                else:
                    self.solverObj.Run()

            self._Time = self._Time + timedelta(minutes=self._mStepRes)
            self._Logger.debug(f"CYMEPY time: {self._Time}")
        elif self.Settings['project']["simulation_type"] == "Static":
            raise Exception("'increment' method cannot be used in QSTS mode")

        return

    def resolve(self):
        self.solverObj.Run()
        self._Logger.debug(f"Resolving at time: {self._Time}")

    def SimulationSteps(self):
        Minutes = (self._EndTime - self._StartTime).total_seconds() / 60.0
        Steps = math.ceil(Minutes / self._mStepRes)

        return Steps, self._StartTime, self._EndTime

    def GetTotalSeconds(self):
        return (self._Time - self._StartTime).total_seconds()

    def GetDateTime(self):
        return self._Time