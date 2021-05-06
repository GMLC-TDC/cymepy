from enum import IntEnum, Enum

DEFAULT_PROFILE_SETTINGS = {
        "multiplier": 1,
        "normalize": False,
        "interpolate": False
    }

PROPERTY_MAP = {
    "kw": "ActiveGeneration",
    "pf": "PowerFactor",
}


FIELD_MAP = {
    "SpotLoad": {
        "kw": [
            "CustomerLoads.Get(",
            ").CustomerLoadModels.Get(1)"
        ],
        "kva": [
            "CustomerLoads.Get(",
            ").CustomerLoadModels.Get(1)",
        ],
        "kvar": [
            "CustomerLoads.Get(",
            ").CustomerLoadModels.Get(1)"
        ],
    },
    "Photovoltaic": {
            "ActiveGeneration": "GenerationModels.Get(1)",
            "PowerFactor": "GenerationModels.Get(1)"
    },
}



class PROFILE_SOURCE_TYPES(Enum):
    HDF5 = "HDF5"
    CSV = "CSV"


class PROFILE_TYPES(IntEnum):
    Load = 0
    Generation = 1
    Irradiance = 2
    Temperature = 3
    Voltage = 4
    Current = 5
    EM_Price = 6
    AS_Price = 7
    WindProfile = 8

    @staticmethod
    def names():
        return list(map(lambda c: c.name, PROFILE_TYPES))

    @staticmethod
    def values():
        return list(map(lambda c: c.value, PROFILE_TYPES))
