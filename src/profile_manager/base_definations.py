from src.profile_manager.common import FIELD_MAP, PROPERTY_MAP
from src.common import CORE_CYMEPY_PROJECT_FILES
import numpy as np
import toml
import abc
import os

import logging
logger = logging.getLogger(__name__)

class BaseProfileManager(abc.ABC):
    def __init__(self, sim_instance, solver, options, logger, **kwargs):
        self.sim_instance = sim_instance
        self.options = options
        self.solver = solver
        self.logger = logger
        self.kwargs = kwargs
        if not options["profiles"]["is_relavtive_path"]:
            self.basepath = options["profiles"]["source"]
        else:
            self.basepath = os.path.join(
                options["project"]["project_path"], options["profiles"]["source"]
            )
        self.mapping_file = os.path.join(
            options["project"]["project_path"], CORE_CYMEPY_PROJECT_FILES.MAPPING_FILE.value
        )
        self.Profiles = {}
        self.mapping = toml.load(open(self.mapping_file , "r"))
        self.sTime = None
        self.eTime = None
        self.simRes = None
        pass

    @abc.abstractmethod
    def setup_profiles(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass


class BaseProfile(abc.ABC):
    def __init__(self, sim_instance, dataset, devices, solver, mapping_dict, logger, **kwargs):
        self.sim_instance = sim_instance
        self.mapping_dict = mapping_dict
        self.dataset = dataset
        self.devices = devices
        self.logger = logger
        self.solver = solver

        pass

    @abc.abstractmethod
    def update_profile_settings(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    def write(self, value, value1):
        for objName, obj in self.devices.items():
            class_name, element_name = objName.split(".")
            if self.valueSettings[objName]['interpolate']:
                value = value1
            mult = self.valueSettings[objName]['multiplier']
            if self.valueSettings[objName]['normalize']:
                valueF = value / self.attrs["max"] * mult
            else:
                valueF = value * mult
            if isinstance(self.attrs["units"], np.ndarray):
                unit = self.attrs["units"][0].decode()
            else:
                unit = self.attrs["units"].decode()

            phases = self.sim_instance.study.QueryInfoDevice("LoadPhase", obj.DeviceNumber, obj.DeviceType)
            phasesType = self.sim_instance.study.QueryInfoDevice("LoadPhaseType", obj.DeviceNumber, obj.DeviceType)
            if phasesType == 'ByPhase':
                phases = [Ph for Ph in phases]
                loadMult = 1 / len(phases)
            else:
                phases = [phases]
                loadMult = 1

            if obj.DeviceType in self.isLoad:
                ppty = FIELD_MAP[class_name][unit]
                key = f"{ppty[0]}{obj.DeviceNumber}{ppty[1]}.LoadValueType"
                loadtype = obj.GetValue(key).lower()

                if unit not in loadtype.split("_"):
                    self.logger.warning(
                        f"{class_name}.{element_name} is of type {loadtype}. A {unit} profile has been attached.Value could not be updated.")
                else:
                    load = self.sim_instance.study.GetLoad(obj.DeviceNumber, self.sim_instance.enums.LoadType.Spot)
                    for ph in phases:
                        en = getattr(self.sim_instance.enums.Phase, ph)
                        load.SetValue(valueF * loadMult, f"LoadValue.{unit.upper()}", obj.DeviceNumber, en, "DEFAULT")
                        kw = load.GetValue(f"LoadValue.{unit.upper()}", obj.DeviceNumber, en, "DEFAULT")

            if obj.DeviceType is self.sim_instance.enums.DeviceType.Photovoltaic:
                if unit in PROPERTY_MAP:
                    relevant_ppty = PROPERTY_MAP[unit]
                    key = FIELD_MAP[class_name][relevant_ppty]
                    obj.SetValue(valueF * loadMult, f"{key}.{relevant_ppty}")
                else:
                    self.logger.warning(f"Units defined for {unit} are  invalid for obj type {class_name}")

            if obj.DeviceType is self.sim_instance.enums.DeviceType.Source:
                Phases = ["A", "B", "C"]
                V = valueF * loadMult
                if unit.lower() == "kvll":
                    V = valueF * loadMult / 1.732
                elif unit.lower() == "kvln":
                    V = valueF * loadMult
                for pha in Phases:
                    ppty = f"OperatingVoltage{pha}"
                    obj.SetValue(V, ppty)
                    logger.info(f"Property {ppty} updated to {V} for {obj.DeviceType}.{obj.DeviceNumber} ")
        return valueF
