import enum


DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

CYMEPY_FOLDER_STRUCTURE = ["model", "logs", "exports"]

class CORE_CYMEPY_PROJECT_FILES(enum.Enum):
    SIMULATION_FILE = "Settings.toml"
    PUBLICATION_FILE = "Publications.toml"
    SUBSCRIPTION_FILE = "Subscriptions.toml"
    PROFILE_MAPPING = "Mapping.toml"
    PROFILES = "Profiles.hdf5"


DEVICES_WITH_MEMORY = {
    'BESS': [],
    'Battery': [],
    'Regulator': ["RegTapA", "RegTapB", "RegTapC"],
    'ShuntCapacitor': ["CapStatus"],
}

