from cymepy.common import CORE_CYMEPY_PROJECT_FILES
import toml
import abc
import os
import re

import logging
logger = logging.getLogger(__name__)

class ExportManager(abc.ABC):
    def __init__(self, sim_instance, solver, options, logger, **kwargs):
        self._Logger = logger
        self.cympy = sim_instance
        self.settings = options
        self.solver = solver
        pubpath = os.path.join(
            self.settings["project"]['project_path'],
            CORE_CYMEPY_PROJECT_FILES.EXPORT_FILE.value
        )
        exportDict = toml.load(open(pubpath, "r"))

        self.validTypes = []
        for k, v in self.cympy.enums.DeviceType.__dict__.items():
            if isinstance(v, int):
                self.validTypes.append(k)

        self.Exports = {}
        for cName, exportList in exportDict.items():
            for exportInfo in exportList:
                if cName not in self.validTypes:
                    raise Exception(f"{cName} is not a valid CYME device type. "
                                    f"For valid device type, see cympy.enums.DeviceType")
                else:
                    devType = getattr(self.cympy.enums.DeviceType, cName)
                    devices = self.cympy.study.ListDevices(devType)
                    if devices:
                        for device in devices:
                            eName = device.DeviceNumber
                            if exportInfo["regex_filter"]:
                                pattern = re.compile(exportInfo["regex_filter"])
                                matches = pattern.search(eName)
                                if matches:

                                    self.create_export_list(exportInfo, device, cName, eName)
                            else:
                                self.create_export_list(exportInfo, device, cName, eName)
                    else:
                        self._Logger.warn(f"Model of type {cName} not found in the distribution model")

        return

    def create_export_list(self, pubInfo, device, cName, eName):
        if cName not in self.Exports:
            self.Exports[cName] = {}
        if eName not in self.Exports[cName]:
            self.Exports[cName][eName] = {
                "device": device,
                "regex": pubInfo['regex_filter'],
                "properties": pubInfo['properties'],
            }
        return

    @abc.abstractmethod
    def update(self):
        time = self.solver.GetDateTime().isoformat()
        results = {time: {}}
        for cName, cInfo in self.Exports.items():
            if cName not in results[time]:
                results[time][cName] = {}
            for eName, einfo in cInfo.items():
                if eName not in results[time][cName]:
                    results[time][cName][eName] = {}
                for ppty in einfo['properties']:
                    if ppty not in results[time][cName][eName]:
                        results[time][cName][eName][ppty] = None
                    device = einfo['device']
                    keyword = self.cympy.app.GetKeyword(ppty)
                    if keyword:
                        res = self.cympy.study.QueryInfoDevice(ppty, device.DeviceNumber, device.DeviceType)
                    else:
                        res = device.GetValue(ppty)
                    results[time][cName][eName][ppty] = res
        return results

