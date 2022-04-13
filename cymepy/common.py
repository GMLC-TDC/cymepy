import enum


DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
DATE_FORMAT2 = '%Y-%m-%d %H:%M:%S'
EXPORT_FILENAME = "Results"
CYMEPY_FOLDER_STRUCTURE = ["model", "logs", "exports"]

class CORE_CYMEPY_OPTIONAL_PROJECT_FILES(enum.Enum):
    MAPPING_FILE = ""
    PROFILES = ""

class CORE_CYMEPY_PROJECT_FILES(enum.Enum):
    SIMULATION_FILE = "Settings.toml"
    PUBLICATION_FILE = "Publications.toml"
    SUBSCRIPTION_FILE = "Subscriptions.toml"    
    EXPORT_FILE = "Exports.toml"

DEVICES_WITH_MEMORY = {
    'BESS': [],
    'Battery': [],
    'Regulator': ["RegTapA", "RegTapB", "RegTapC"],
    'ShuntCapacitor': ["CapStatus"],
}

