from src.profile_manager.common import PROFILE_TYPES, DEFAULT_PROFILE_SETTINGS, UNITS_MAP, CLASS_MAP
from src.profile_manager.base_definations import BaseProfileManager, BaseProfile
from src.common import DATE_FORMAT
import pandas as pd
import datetime
import pyodbc
import copy
import os
class ProfileManager(BaseProfileManager):

    time_mapping = {
        "1MINUTE": 1,
        "5MINUTES": 5,
        "10MINUTES": 10,
        "15MINUTES": 15,
        "30MINUTES": 30,
        "1HOUR": 60,
    }

    def __init__(self, sim_instance, solver, options, logger, **kwargs):
        super(ProfileManager, self).__init__(sim_instance, solver, options, logger, **kwargs)
        self.DRV = options["profiles"]["settings"]["driver"]
        self.PWD = options["profiles"]["settings"]["password"]
        self.freq = {}
        if self.PWD:
            self.con = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(self.DRV, self.basepath, self.PWD))
        else:
            self.con = pyodbc.connect('DRIVER={};DBQ={}'.format(self.DRV, self.basepath))
        self.cur = self.con.cursor()
        self.setup_profiles()
        pass

    def setup_profiles(self):
        data = {}
        for dTtype, tblname in self.options["profiles"]["tables"].items():
            self.freq[dTtype] = self.time_mapping[tblname.split("_")[2]]
            SQL = f'SELECT * FROM {tblname};'  # your query goes here
            pData= pd.read_sql(SQL, self.con)
            year = min(set(pData.ProfileYear.tolist()))
            hour = min(set(pData.YearIntervalNumber.tolist())) - 1
            IDS = set(pData.ID.tolist())
            elements = {}
            for id in IDS:
                elements[id] = {}
                profileData = pData[pData["ID"] == id]
                for unit in set(profileData.Unit.tolist()):
                    element_unit_data = profileData[profileData["Unit"] == unit]
                    values = ";".join(element_unit_data.ValuesX.to_list())
                    values = [float(v) for v in values.split(";")]
                    elements[id][unit] = values

            dict_of_df = {k: pd.DataFrame(v) for k, v in elements.items()}
            elements = pd.concat(dict_of_df, axis=1)
            elements.index = pd.Timestamp(f'{year}-01-01')+pd.to_timedelta(elements.index * self.freq[dTtype], unit="m")
            data[dTtype] = elements

        for eType, eData in data.items():
            for elm_name, unit_id in eData.columns:
                values = eData[elm_name][unit_id]
                device = self.get_device(eType, elm_name)
                #print(eType, elm_name, device)
                if device:
                    cName = CLASS_MAP[device.DeviceType]
                    devices = {
                        f"{cName}.{device.DeviceNumber}": device
                    }
                    self.Profiles[f"{cName}/{device.DeviceNumber}/{UNITS_MAP[int(unit_id)]}"] = Profile(
                        self.sim_instance,
                        values,
                        devices,
                        self.solver,
                        None,
                        self.logger,
                        **{
                            "type": f"{cName}",
                            "name": f"{device.DeviceNumber}",
                            "unit": f"{UNITS_MAP[int(unit_id)]}",
                        }
                    )

    def update(self):
        results = {}
        for profileaName, profileObj in self.Profiles.items():
            result = profileObj.update()
            results[profileaName] = result
        return results

    def get_device(self, dTtype, id):
        devType = getattr(self.sim_instance.enums.DeviceType, dTtype)
        devices = self.sim_instance.study.ListDevices(devType)
        for device in devices:
            if id == device.DeviceNumber:
                return device
        return None

class Profile(BaseProfile):
    def __init__(self, sim_instance, dataset, devices, solver, mapping_dict, logger, **kwargs):
        super(Profile, self).__init__(sim_instance, dataset, devices, solver, mapping_dict, logger, **kwargs)
        name = list(devices.keys())[0]
        self.valueSettings = {name: DEFAULT_PROFILE_SETTINGS}
        self.attrs = {
            "sTime": self.dataset.index.min(),
            "eTime": self.dataset.index.max(),
            "units": kwargs['unit'].encode(),
            "info": "",
            "mean": self.dataset.mean(),
            "min": self.dataset.min(),
            "max": self.dataset.max(),
            "npts": len(self.dataset),
            "resTime": 3600,

        }
        self.logger.info(f"Profile '{kwargs['type']}' created and connect tp ppty '{kwargs['unit']}' of device'{kwargs['name']}' ")

    def update_profile_settings(self):
        pass

    def update(self):
        self.Time = copy.deepcopy(self.solver.GetDateTime())
        if self.Time < self.dataset.index.min() or self.Time > self.dataset.index.max():
            value = 0
        else:
            value = self.dataset[self.Time]
        value = self.write(value, value)
        return value