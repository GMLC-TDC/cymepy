from src.profile_manager.common import PROFILE_TYPES, DEFAULT_PROFILE_SETTINGS, FIELD_MAP
from src.profile_manager.base_definations import BaseProfileManager, BaseProfile
from src.common import DATE_FORMAT
import datetime
import h5py
import copy
import os

class ProfileManager(BaseProfileManager):
    def __init__(self, sim_instance, solver, options, logger, **kwargs):
        super(ProfileManager, self).__init__(sim_instance, solver, options, logger, **kwargs)
        if os.path.exists(self.basepath):
            self.logger.info("Loading existing h5 store")
            self.store = h5py.File(self.basepath, "r+")
        else:
            self.logger.info("Creating new h5 store")
            self.store = h5py.File(self.basepath, "w")
            for profileGroup in PROFILE_TYPES.names():
                self.store.create_group(profileGroup)
        self.setup_profiles()
        pass

    def setup_profiles(self):

        for group, profileMap in self.mapping.items():
            if group in self.store:
                grp = self.store[group]
                for profileName, mappingDict in profileMap.items():
                    if profileName in grp:
                        devices = self.get_devices(mappingDict)
                        if devices:
                            self.Profiles[f"{group}/{profileName}"] = Profile(
                                self.sim_instance,
                                grp[profileName],
                                devices,
                                self.solver,
                                mappingDict,
                                self.logger,
                                **self.kwargs
                            )
                    else:
                        self.logger.warning("Group {} \ data set {} not found in the h5 store".format(
                            group, profileName
                        ))
            else:
                self.logger.warning("Group {} not found in the h5 store".format(group))
        return
        pass

    def get_devices(self, mappingDict):
        devicesObjects = {}
        for x in mappingDict:
            cName, eName = x['object'].split(".")
            devType = getattr(self.sim_instance.enums.DeviceType, cName)
            devices = self.sim_instance.study.ListDevices(devType)
            found = False
            for device in devices:
                if eName == device.DeviceNumber:
                    devicesObjects[x['object']] = device
                    found = True
                    break
            if not found:
                self.logger.warning(
                    f"Device {eName} of class {cName} defined in the mapping file not found in the loaded model"
                )
        return devicesObjects

    def update(self):
        results = {}
        for profileaName, profileObj in self.Profiles.items():
            result = profileObj.update()
            results[profileaName] = result
        pass

class Profile(BaseProfile):
    def __init__(self, sim_instance, dataset, devices, solver, mapping_dict, logger, **kwargs):
        super(Profile, self).__init__(sim_instance, dataset, devices, solver, mapping_dict, logger, **kwargs)
        self.valueSettings = {x['object']: {**DEFAULT_PROFILE_SETTINGS, **x} for x in mapping_dict}
        self.attrs = self.dataset.attrs
        self.update_profile_settings()
        pass

    def update_profile_settings(self):
        self.sTime = datetime.datetime.strptime(self.attrs["sTime"].decode(), DATE_FORMAT)
        self.eTime = datetime.datetime.strptime(self.attrs["eTime"].decode(), DATE_FORMAT)
        self.simRes, _, _ = self.solver.SimulationSteps()
        self.Time = copy.deepcopy(self.solver.GetDateTime())


    def update(self):
        self.Time = copy.deepcopy(self.solver.GetDateTime())
        if self.Time < self.sTime or self.Time > self.eTime:
            value = 0
            value1 = 0
        else:
            dT = (self.Time - self.sTime).total_seconds()
            n = int(dT / self.attrs["resTime"])
            value = self.dataset[n]
            dT2 = (self.Time - (
                        self.sTime + datetime.timedelta(seconds=int(n * self.attrs["resTime"])))).total_seconds()
            value1 = self.dataset[n] + (self.dataset[n + 1] - self.dataset[n]) * dT2 / self.attrs["resTime"]

        for objName, obj in self.devices.items():
            class_name, element_name = objName.split(".")
            if self.valueSettings[objName]['interpolate']:
                value = value1
            mult = self.valueSettings[objName]['multiplier']
            if self.valueSettings[objName]['normalize']:
                valueF = value / self.attrs["max"] * mult
            else:
                valueF = value * mult
            #ppty = FIELD_MAP[class_name][self.attrs["units"].decode()]
            ppty = f"CustomerLoads.Get({obj.DeviceNumber}).CustomerLoadModels.Get(1).CustomerLoadValues.Get(A).LoadValue.KVA"
            #kw =obj.GetValue(f"CustomerLoads.Get({obj.DeviceNumber}).CustomerLoadModels.Get(1).LoadValueType")
            #print(kw)
            obj.SetValue(valueF, ppty)
            #ppty = f'{ppty[0]}{obj.DeviceNumber}{ppty[1]}'
            #obj.SetValue(valueF, ppty, obj.DeviceNumber, self.sim_instance.enums.Phase.ABC, "DEFAULT")
        return valueF