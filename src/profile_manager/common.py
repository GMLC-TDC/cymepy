from enum import IntEnum, Enum

DEFAULT_PROFILE_SETTINGS = {
        "multiplier": 1,
        "normalize": False,
        "interpolate": False
    }


FIELD_MAP = {
    "SpotLoad": {
        "kw": "LoadValue.KW",
        "kva": "SpotKVAT",
        "kvar": "SpotKVART",
    }
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
