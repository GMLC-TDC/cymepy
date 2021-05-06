import enum


DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
EXPORT_FILENAME = "Results"
CYMEPY_FOLDER_STRUCTURE = ["model", "logs", "exports"]

class CORE_CYMEPY_PROJECT_FILES(enum.Enum):
    SIMULATION_FILE = "Settings.toml"
    PUBLICATION_FILE = "Publications.toml"
    SUBSCRIPTION_FILE = "Subscriptions.toml"
    MAPPING_FILE = "Mapping.toml"
    PROFILES = "Profiles.hdf5"
    EXPORT_FILE = "Exports.toml"


DEVICES_WITH_MEMORY = {
    'BESS': [],
    'Battery': [],
    'Regulator': ["RegTapA", "RegTapB", "RegTapC"],
    'ShuntCapacitor': ["CapStatus"],
}

